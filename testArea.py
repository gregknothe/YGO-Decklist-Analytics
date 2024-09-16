import random as rand
import pandas as pd



name = ["dog", "cat", "dragon", "car"]
type = ["monster", "tuner monster", "spell", "trap"]
tag = ["animal", "animal","dragon","vehicle"]
value = [1,1,2,3]

df = pd.DataFrame({"name": name, "type": type, "tag": tag, "value": value})
#print(df)

#print(df.loc[df["tag"] == "animal"])
#print(df.loc[df["value"] == 1])

x = [1,2,3]
y = [1,2,4]

z = list(set(x)-set(y))
print(z)