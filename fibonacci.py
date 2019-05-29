#input
f0 = 0
f1 = 1

#upper limit
limit = 100

for i in range(limit - 1):
    x = f1 + f0
    f0 = f1
    f1 = x

print('Nr.',i+2)
print(f1)
