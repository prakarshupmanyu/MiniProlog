
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.8'

_lr_method = 'LALR'

_lr_signature = 'FC3D7CE10998C4E8550B5368AA34C0EA'
    
_lr_action_items = {'PREDICATE':([0,3,5,6,7,9,10,13,15,18,21,27,29,31,38,],[1,1,1,12,1,1,1,1,1,1,1,1,1,1,1,]),'CONJUNCTION':([1,4,8,11,19,20,22,23,24,25,32,34,41,44,45,46,47,],[-1,10,-10,18,-2,27,-12,31,-3,-11,-11,-4,-7,-5,-6,-9,-8,]),'RPAREN':([1,4,8,11,12,14,16,17,19,20,22,23,24,25,26,28,30,32,33,34,35,36,37,39,40,41,42,43,44,45,46,47,],[-1,8,-10,8,19,22,24,25,-2,28,-12,8,-3,-11,32,34,36,-11,39,-4,40,41,42,44,45,-7,46,47,-5,-6,-9,-8,]),'LPAREN':([0,3,5,6,7,9,10,13,15,18,21,27,29,31,38,],[3,5,5,13,15,3,3,3,5,3,3,3,3,3,3,]),'NOT':([3,5,13,15,],[6,6,21,6,]),'IMPLIES':([1,4,8,11,19,22,23,24,32,34,41,44,45,46,47,],[-1,9,-10,9,-2,-12,9,-3,-11,-4,-7,-5,-6,-9,-8,]),'DISJUNCTION':([1,4,8,11,19,20,22,23,24,25,32,34,41,44,45,46,47,],[-1,7,-10,7,-2,29,-12,7,-3,-11,38,-4,-7,-5,-6,-9,-8,]),'$end':([1,2,8,19,22,24,25,34,41,44,45,46,47,],[-1,0,-10,-2,-12,-3,-11,-4,-7,-5,-6,-9,-8,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'sentence':([0,3,5,7,9,10,13,15,18,21,27,29,31,38,],[2,4,11,14,16,17,20,23,26,30,33,35,37,43,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> sentence","S'",1,None,None,None),
  ('sentence -> PREDICATE','sentence',1,'p_sentence_predicate','runningCopy_final.py',42),
  ('sentence -> LPAREN NOT PREDICATE RPAREN','sentence',4,'p_sentence_negation','runningCopy_final.py',47),
  ('sentence -> LPAREN sentence IMPLIES sentence RPAREN','sentence',5,'p_sentence_implies','runningCopy_final.py',52),
  ('sentence -> LPAREN NOT LPAREN sentence RPAREN RPAREN','sentence',6,'p_sentence_in_negation','runningCopy_final.py',57),
  ('sentence -> LPAREN NOT LPAREN sentence CONJUNCTION sentence RPAREN RPAREN','sentence',8,'p_sentence_demorgan','runningCopy_final.py',62),
  ('sentence -> LPAREN NOT LPAREN sentence DISJUNCTION sentence RPAREN RPAREN','sentence',8,'p_sentence_demorgan','runningCopy_final.py',63),
  ('sentence -> LPAREN NOT LPAREN NOT sentence RPAREN RPAREN','sentence',7,'p_sentence_double_negation','runningCopy_final.py',72),
  ('sentence -> LPAREN LPAREN sentence CONJUNCTION sentence RPAREN DISJUNCTION sentence RPAREN','sentence',9,'p_sentence_distribute','runningCopy_final.py',77),
  ('sentence -> LPAREN sentence DISJUNCTION LPAREN sentence CONJUNCTION sentence RPAREN RPAREN','sentence',9,'p_sentence_distribute','runningCopy_final.py',78),
  ('sentence -> LPAREN sentence RPAREN','sentence',3,'p_sentence_binary','runningCopy_final.py',87),
  ('sentence -> LPAREN sentence CONJUNCTION sentence RPAREN','sentence',5,'p_sentence_binary','runningCopy_final.py',88),
  ('sentence -> LPAREN sentence DISJUNCTION sentence RPAREN','sentence',5,'p_sentence_binary','runningCopy_final.py',89),
]