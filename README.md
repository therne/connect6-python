# Connect6 for Python 
[Connect6](https://en.wikipedia.org/wiki/Connect6) game implemented in Python.  
This is not for playable purpose - rather, it's tool for experiment and developing Connect6 AI. 

![Screenshot](http://i.imgur.com/nhqJCYF.png)


## Features

* It's Python. NOTE THAT Python is cool and awesome.
* Bot (AI) implementation / test support
  * You can implement, test, and match with your own bots.
* Game record logging

## Prerequisites

* Python 3

## Usage
In non-windows OS, just:
```
$ ./game.py
```

In Windows, Please use Python 3 interpreter explicitly.

```
> python3 game.py
```


## How to implement bot?

First, implement your own bot. Then modify `config.py` :

```python
from my_awesome_bot import MyAwesomeAIBot

# change AIBot to your bot.
AIBot = MyAwesomeAIBot
```

Also, you can modify `game.py` to support multiple bots.

## Logging

After you played game, the gameplay log will be stored in `logs/` directory.  
A log is like this: 

```python
("Move",2,6,5) # Black at G6 (6,5)
("Move",1,0,3) # White at A4 (0,3)
("Move",1,0,4) # White at A5 (0,4)
("Res", 1) # White won.
```
As you can see, it's python code. You can read and process the log data by evaluating them line by line.


## License: MIT
