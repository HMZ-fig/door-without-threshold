import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
s = json.load(open(os.path.join(os.path.dirname(HERE), 'data', 'scope.json'), encoding='utf-8'))
key = sys.argv[1]
print(s['counts'].get(key, 'NONE'))