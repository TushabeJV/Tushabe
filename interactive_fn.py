# Greet the user
print("Hi!")

name = input("What's your name? ") # ask the user their name

print("It's nice to meet you,", name)
answer = input("Are you enjoying the course? ")

if answer.lower() == ("yes"):
    print("That's good to hear!")
else:
    print("Oh no! That makes me sad!")
