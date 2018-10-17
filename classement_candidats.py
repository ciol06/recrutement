#python3 classement_candidats.py 

filiere = 'MPSI' # 'PCSI'

# classement des candidats a partir du fichier cvs (venant de xls)
# et des dossiers pdf


# 
# ne pas oublier d'enregistrer candidats.csv en utf8
# séparateur de champ ; séparateur de texte rien
# le champ avisdossier est à ajouter au fichier de l'administration
# fichier: PCSI.csv ou MPSI.csv
nchamps = {'numero': 3,'avisdossier':5,
           'nom':4,'prenom':5,'sexe':7,
           'francE':73,'francO':72,
           'lycee':13,'nivclas':25,
           'avisCE':26,
           'mathsN':27,'mathsR':28,'mathsE':29,
           'physN':30,'physR':31,'physE':32,
           'philN':45,'philR':46,'philE':47,
           'lv1N':39,'lv1R':40,'lv1E':41,
           'mathsT1':104,'mathsT2':149,'mathsT3':194, # note du candidat
           'mathsT1c':105,'mathsT2c':150,'mathsT3c':195, # moyenne de la classe
           'mathsT1t':106,'mathsT2t':151,'mathsT3t':196, #saisie: CAN ou ETA
           'physT1':107,'physT2':152,'physT3':197,
           'physT1c':108,'physT2c':153,'physT3c':198,
           'physT1t':109,'physT2t':154,'physT3t':199,
}

champstexte = ['numero', 'nom','prenom','sexe','lycee','nivclas','avisCE',
               'mathsT1t','mathsT2t','mathsT3t',
               'physT1t','physT2t','physT3t',]

def to_float(s):
  try:
    return(float(s.replace(',','.')))
  except:
    return(0)

from dossiers import mauvaispoints

if filiere == 'MPSI':
  mauvaispoints = []

def previsions():
  dp = {}
  f = open('previsions_2018_8966_5_groupes.csv','r')
  for l in f.readlines():
      l = l.replace('\n','')
      np,g,m = l.split(';')
      dp[np] = g
  f.close()
  return(dp)

groupes = previsions()

def lit_fichier_candidats(fichier):
  f = open(fichier,'r')
  lc = []
  for l in f.readlines():
      l = l.replace('\n','')
      lc.append(l.split(';'))
  print(lc[0],len(lc[0]))
  d = {}
  for c in lc[1:]:
    n = c[nchamps['numero']]
    d[n] = c
  l = []
  dc = {}
  for c in lc[1:]:
    cc = {}
    for champ in nchamps :
      nc = nchamps[champ]
      if champ in champstexte:
        cc[champ] = c[nc]
      else:
        cc[champ] = to_float(c[nc])
    bavard = 0
    np = cc['nom'] + ' ' + cc['prenom']
    tm = 0
    for m in mauvaispoints:
      if np in mauvaispoints[m]:
        mp = mauvaispoints[m][np]
        print(m, np, mp)
        cc[m] = mp
        tm = tm + mp
    cc['total mots'] = tm
    try:
      cc['groupe DL'] = groupes[np] # groupe deep learning
    except:
      cc['groupe DL'] = '?'
    l.append(cc)
    dc[cc['numero']] = cc
  return(lc[0],l,d,dc)

lchamps,lcandidats,tout, toutc = lit_fichier_candidats(filiere + '.csv')

for i,c in enumerate(lchamps):
  print(i,c)

def notefinale(c):
  if filiere == 'PCSI':
    cmath = 1
  else:
    cmath = 2
  notescience = (cmath * c['mathsN'] + c['physN'])/(1 + cmath)
  if notescience == 0:
    if (c['mathsT1t'] == 'ETA' and c['mathsT2t'] == 'ETA'
        and c['physT1t'] == 'ETA' and c['physT2t'] == 'ETA'):
      notescience = (cmath * (c['mathsT1'] + c['mathsT2'])
                     + c['physT1'] + c['physT2'] )/(2 * cmath + 2)
  note = (30 * notescience
       + (3*c['francE'] + c['francO'] + c['philN'])
       + 5*c['lv1N'])/40
  rangscience = (cmath * c['mathsR'] + c['physR'])/(1 + cmath)
  effectifscience = (cmath * c['mathsE'] + c['physE'])/(1 + cmath)
  noteclasse = 10
  if c['mathsR']*c['physR']*c['mathsE']*c['physE'] != 0:
      if c['nivclas'] == 'Faible': noteclasse = 8
      if c['nivclas'] == 'Moyen': noteclasse = 10
      if c['nivclas'] == 'Assez bon': noteclasse = 11
      if c['nivclas'] == 'Bon': noteclasse = 12
      if c['nivclas'] == 'Très bon': noteclasse = 13
      rangnormalise = (effectifscience-rangscience+1)/effectifscience
      noteattendue = noteclasse + 2*(rangnormalise - 0.5)*(18-noteclasse)
      if abs(noteattendue - notescience) > 3:
        print('pb notation: ')
        print(c['nom'],notescience,noteattendue,note,
              rangscience,effectifscience,
              noteclasse,c['lycee'])
        c['pbnotation'] = 1
      else:
        c['pbnotation'] = 0
      c['notefinale'] = note
      c['notescience'] = notescience
  else:
    c['notefinale'] = notescience
    c['notescience'] = notescience
  return(c)

lchamps2 = ['pbnotation','notefinale','notescience','groupe DL',
            'avisdossier'] + [m for m in mauvaispoints] + ['total mots']

def to_floatf(s):
  try:
    return(str(s).replace('.',','))
  except:
    return(0)

def cree_fichier_candidats_completes(fichier):
    for c in lcandidats:
        c['notefinale'] = 0
        notefinale(c)
        if toutc[c['numero']]['notefinale'] != c['notefinale']:
          print('========== probleme: ',c)
    f = open(fichier,'w')
    l = ''
    for champ in lchamps2 + lchamps:
        l = l + champ + ';'
    l = l + '\n'
    f.write(l)
    lnc = [nc for nc in tout]
    lnc = sorted(lnc, key = lambda x: - toutc[x]['notefinale'])
    print(lnc)
    for nc in lnc:
        c = tout[nc]
        cc = toutc[nc]
        #print(nc,cc['nom'])
        l = ''
        for y in lchamps2:
            try:
                l = l  + to_floatf(cc[y]) + ';'
            except:
                l = l  + '' + ';'
        for x in c:
            l = l + to_floatf(x) + ';'
        l = l + '\n'
        f.write(l)
    f.close()

cree_fichier_candidats_completes('candidatscompletes' + filiere + '.csv')
