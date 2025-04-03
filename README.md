# Gemini Post Maker  
Generates a matchday overview automatically.

# Proces (generator.py)  
1. import libraries  
2. creates a class to store match data  
3. creates a function that gets the title of the matchday
4. creates a function that centers text horizontally  
5. creates a function that draws a match on the image  
6. creates a function that loads the matches from online sources  
7. creates a function that puts all the text and icons together as 1 image  
8. creates a function that normalizes official team names  
9. creates a function that gets the city based on the normalized team name  
10. creates a function that displays error messages  
11. creates a function that displays succes messages  
12. load city names from json  
13. load matches from online sources  
14. load images from /res folder  
15. load fonts  
16. calculate how many posts to make  
17. make that amount of posts  

# Logic  
- `Amount of posts to make = matches // 3 (+1 if matches%3>0)`  
- `Amount of matches on current post = 3 if len(matches) - (index * 3) >= 3 else len(matches) % 3`  

# Libraries  
- os -> to clear screen  
- re -> to normalize team names  
- json -> to translate teams to cities  
- datetime -> to get the date names  
- requests -> to get the matches from online sources  
- PIL -> to generate the post using text and images  
- bs4 -> to find the matches inside the html code of the requests  