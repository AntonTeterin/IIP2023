import json

with open('counts.json') as f:
    counts = [tuple(x) for x in json.loads(f.read())]

all_c = 0
post_c = 0
comm_c = 0
all_p_c = 0
for i, p, all_p, g, c in counts:
    post_c += p
    all_p_c += all_p
    all_c += g
    comm_c += c
print(post_c, all_p_c, all_c - post_c, comm_c)