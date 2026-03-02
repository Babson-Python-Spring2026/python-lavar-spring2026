# Goal: Keep asking until valid integer
# Keep asking for an integer until the user enters a valid one.

prompt = 'Enter an integer'
while True:

    try:
        x = int(input(prompt))
    except ValueError:
        prompt = 'listen dummy, enter integer'
    else:
        print(x)
        break