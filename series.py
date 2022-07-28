num = 1
chance = 2/3
currentChance = 2/3

while num < 2.99:
    num += currentChance
    currentChance *= chance
    print(num, currentChance)