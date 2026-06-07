INCLUDE = ["del*", "test*"]
EXCLUDE = ["logs*", "del*"]


print([val for val in EXCLUDE if val in INCLUDE])