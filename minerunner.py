# 1280 x 720

import tkinter as tk
import random as rand
import time, csv

from tkinter.filedialog import askopenfilename

import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)
 

# Base class that hosts the tkinter window
class App(tk.Tk):

	def __init__(self):
		tk.Tk.__init__(self)

		self.username = tk.StringVar(value="GUEST-000")
		self.levelprogression = ["Levels:"] + ["0"]*24
		self.randomscores = ["0"]*3
		self.randomtitles = ["Easy", "Medium", "Hard"]

		self.title("Minerunner")
		self.geometry(f"{width}x{height}")

		self.bind("<Control-c>", self.bossKey)
		self.boss = False

		self.pages = {}
		for P in {MainMenu, LevelPage, BossPage, NamePromt}:
			page = P(self)
			self.pages[P] = page
			self.pages[P].grid(row=0, column=0, sticky="nsew")
		self.showPage(NamePromt)

	def showPage(self, page):   # allows the page being displayed to be changed from any page
		if page == MainMenu:
			self.pages[page].colourLevelButtons()
		self.pages[page].tkraise()

	def bossKey(self, *e):      # switches between boss key page and main menu
		if self.boss:
			self.boss = False
			self.title("Minerunner")
			self.showPage(MainMenu)
		else:
			self.boss = True
			self.title("Excel")
			self.showPage(BossPage)

# Window that allows user to input thier username or load a game
class NamePromt(tk.Frame):

	def __init__(self, app):
		tk.Frame.__init__(self, app, width=width, height=height)
		self.pack_propagate(0)
		self.app = app

		self.logo_image = tk.PhotoImage(file="images/logo.png")
		tk.Label(self, image=self.logo_image).pack(pady=(10, 80))

		font = ("Verdana", 24)
		tk.Label(self, text="Enter your name:", font=font).pack(pady=10)
		self.name_entry = tk.Entry(self, font=font)
		self.name_entry.bind("<Return>", self.startGame)
		self.name_entry.pack(pady=5)
		tk.Button(self, text="Start!", command=self.startGame, font=font).pack(pady=10)

		tk.Button(self, text="Load Save", command=self.loadGame, font=font).pack(side="bottom", pady=100)

		self.name_entry.focus_set()

	def startGame(self, *e):            # loads the username entered (or assignes one) and shows the main menu
		name = self.name_entry.get()
		if name != self.app.username.get():
			if name:
				self.app.username.set(name.upper())
			else:
				self.app.username.set("GUEST-" + str(rand.randint(100, 1000)))
			self.app.levelprogression = ["Levels:"] + ["0"]*24
			self.app.randomscores = ["0"]*3
		self.app.showPage(MainMenu)

	def loadGame(self, *e):             # loads game data from an external file and shows the main menu
		filename = tk.filedialog.askopenfilename(filetypes=[('text files', '*.txt'), ('All files', '*.*')])
		if filename:
			with open(filename, "r") as f:
				loaded = f.read().split("\n")
			self.app.username.set(loaded[0].upper())
			self.app.levelprogression = loaded[1].split(",")
			self.app.randomscores = loaded[2].split(",")
			self.app.showPage(MainMenu)

# Window with level select and leaderboards
class MainMenu(tk.Frame):

	def __init__(self, app):
		tk.Frame.__init__(self, app, width=width, height=height)
		self.pack_propagate(0)
		self.app = app

		self.leaderboard = tk.Canvas(self)
		self.showLevelLeaderboard(1)

		self.logo_image = tk.PhotoImage(file="images/logo.png")
		tk.Label(self, image=self.logo_image).pack(pady=10, side="top")

		self.levelselect = self.levelSelectCanvas()
		self.levelselect.pack(side="left", padx=(130, 1))

		tk.Label(self, text="Playing as: ", font=("Verdana", 15)).place(x=20, y=20)
		tk.Label(self, textvar=self.app.username, font=("Verdana", 15, "bold")).place(x=160, y=20)
		tk.Button(self, text="Change Account", command=self.changeAccount).place(x=20, y=60)

		tk.Button(self, text="Save Progress", font=("Verdana", 13), command=self.saveProgress).place(x=width-20, y=20, anchor="ne")

	def levelSelectCanvas(self):          # creates a tkinter canvas displaying buttons to each level
		self.levelButtons = [None]*24
		canvas = tk.Canvas(self)
		font = ("Verdana", 24)
		tk.Label(canvas, text="Level Select:", font=font).grid(row=0, column=0, columnspan=6)
		for lvl in range(24):
			b = tk.Button(canvas, text=lvl+1, width=3, font=font, bg="gray", state="disabled", command=lambda x=lvl+1: self.showLevelLeaderboard(x))
			self.levelButtons[lvl] = b
			self.levelButtons[lvl].grid(row=lvl//6+1, column=lvl-(lvl//6)*6, padx=1, pady=1)
		self.colourLevelButtons()
		tk.Label(canvas, text="Random Levels:", font=font).grid(row=5, column=0, columnspan=6)
		lvl_names = ["Easy", "Medium", "Hard"]
		lvl_colours = ["#C0C2E2", "#E0747D", "#CE3141"]
		for i in range(3):
			b = tk.Button(canvas, text=lvl_names[i], width=7, font=font, bg=lvl_colours[i], command=lambda x=lvl_names[i]: self.showLevelLeaderboard(x))
			b.grid(row=6, column=2*i, columnspan=2, padx=1, pady=1)
		return canvas

	def colourLevelButtons(self, *e):      # colours the buttons on the level select based on if the user has completed them, or if they are available
		self.showLevelLeaderboard(1)
		for i in range(24):
			colour = "#272F38"
			self.levelButtons[i].configure(state="disabled")
			if self.app.levelprogression[i+1] != "0":
				colour = "#5EC171"
				self.levelButtons[i].configure(state="normal")
			elif self.app.levelprogression[i] != "0":
				colour = "#DEE5E5"
				self.levelButtons[i].configure(state="normal")
				self.showLevelLeaderboard(i+1)
			self.levelButtons[i].configure(bg=colour)

	def showLevelLeaderboard(self, n):     # displays the leaderboard and user's score for the currently selected level
		bgcol = "#E1E5ED"
		font = ("Verdana", 24)

		self.leaderboard.destroy()
		self.leaderboard = tk.Canvas(self, width=400, height=480, bg=bgcol)
		self.leaderboard.pack_propagate(0)
		self.leaderboard.pack(side="right", padx=(1, 130))

		if n in ["Easy", "Medium", "Hard"]:
			title = "Random: " + n
		else:
			title = "Level " + str(n)
		tk.Label(self.leaderboard, text=title, font=font, bg=bgcol).pack(pady=20)
		if n in self.app.randomtitles:
			if self.app.randomscores[self.app.randomtitles.index(n)] != "0":
				tk.Label(self.leaderboard, text="Best Time: "+self.app.randomscores[self.app.randomtitles.index(n)], font=("Verdana", 14), bg=bgcol).pack()
			else:
				tk.Label(self.leaderboard, text="Not Played", font=("Verdana", 14), bg=bgcol).pack()
		else:
			if self.app.levelprogression[n] != "0":
				tk.Label(self.leaderboard, text="Best Time: "+self.app.levelprogression[n], font=("Verdana", 14), bg=bgcol).pack()
			else:
				tk.Label(self.leaderboard, text="Not Played", font=("Verdana", 14), bg=bgcol).pack()

		self.createLeaderboard(self.leaderboard, n, bgcol).pack(pady=15)

		tk.Button(self.leaderboard, text="Play", font=("Verdana", 18), bg="#ABB7D6", command=lambda x=n: self.startLevel(n)).pack(pady=20)

	def createLeaderboard(self, c, n, background):   # creates the leaderboard for the level by reading an external file
		l_canvas = tk.Canvas(c, height=10, bg=background, bd=0, highlightthickness=0)
		with open(f"leaderboards/level{n}.csv", newline="") as f:
			leaderboard = csv.reader(f)
			for i, row in enumerate(leaderboard):
				if i == 6:
					break
				bgcol = background
				time, name = row
				if name == self.app.username.get():
					bgcol = "white"
				text = f"{i+1}| {time} : {name}".ljust(23)
				tk.Label(l_canvas, text=text, font=("Consolas", 17), bg=bgcol).grid(row=i, column=0, sticky="w")
		return l_canvas

	def startLevel(self, n):     # changes the level loaded on the level page to the newly selected one and shows the page
		self.app.pages[LevelPage].changeLevel(n)
		self.app.showPage(LevelPage)

	def changeAccount(self):     # returns to the name entry page (inserts current name to entry box incase of missclick)
		current_name = self.app.username.get()
		self.app.pages[NamePromt].name_entry.delete(0, "end")
		self.app.pages[NamePromt].name_entry.insert(0, current_name)
		self.app.showPage(NamePromt)

	def saveProgress(self):      # saves the users progress by writing to an external file
		filename = f"{self.app.username.get()}-progress.txt"
		with open(filename, "w") as f:
			data = [self.app.username.get(), ",".join(self.app.levelprogression), ",".join(self.app.randomscores)]
			f.write('\n'.join(data))
		self.saved_label = tk.Label(self, text="Progress Saved!", font=("Verdana", 16), fg="green")
		self.saved_label.place(x=width-20, y=60, anchor="ne")
		self.app.after(4000, self.saved_label.place_forget)

# Hosts the current game level
class LevelPage(tk.Frame):

	def __init__(self, app):
		tk.Frame.__init__(self, app, width=width, height=height)
		self.pack_propagate(0)
		self.app = app

		sfont = ("Verdana", 16)
		self.timestr = tk.StringVar(value="00:00")
		self.timing = False
		self.cpause = False
		self.cheat_time = 0
		self.paused_time = [0, 0]
		self.final_time = "00:00"

		self.timevalue = tk.StringVar(value="in 0:00.000")
		self.won_text = tk.Label(self, text=" You Won! ", font=("Verdana", 28), bg="#333F68", fg="#5DD32A")
		self.lost_text = tk.Label(self, text=" You Lost ", font=("Verdana", 28), bg="#333F68", fg="#CC2828")
		self.time_text = tk.Label(self, textvar=self.timevalue, font=("Verdana", 16), bg="#333F68", fg="#5DD32A")
		self.nextlevel_button = tk.Button(self, text="Next Level", font=("Verdana", 12), command=self.nextLevel)
		self.retry_button = tk.Button(self, text="Retry", font=("Verdana", 12), command=self.restartButton)

		self.title = tk.StringVar(value="Level 1")
		tk.Label(self, textvar=self.title, font=("Verdana", 28)).pack(pady=20)

		self.game_canvas = tk.Canvas(self, bd=0, highlightthickness=0)
		self.game_canvas.pack(pady=15)

		data_bar = tk.Frame(self.game_canvas)
		data_bar.pack(fill="x", pady=10)

		self.clock = tk.Label(data_bar, font=sfont, textvar=self.timestr)
		self.clock.pack(side="left")
		tk.Button(data_bar, text="↺", font=("Verdana", 14), width=3, command=self.restartButton).pack(side="right")
		tk.Button(data_bar, text="⏸︎", font=("Calibri", 14), width=3, command=self.pauseButton).pack(side="right", padx=5)
		self.paused_text = tk.Label(self, text="Paused", font=("Verdana", 28))

		tk.Button(self, text="<", font=("Verdana", 14), command=self.back).place(x=10, y=10)

		self.currentLvl = 1
		self.minerunner = tk.Canvas(self)
		self.changeLevel(1)

	def changeLevel(self, n):     # clears the page of labels and canvass before creating a new minerunner object of the new level
		self.forgetTopText()
		self.resetTimer()
		self.currentLvl = n
		if n in ["Easy", "Medium", "Hard"]:
			t = "Random: " + n
		else:
			t = "Level " + str(n)
		self.title.set(t)

		self.minerunner.destroy()
		self.minerunner = minerunnerCanvas(self.game_canvas, self, n)
		self.minerunner.pack()
		self.minerunner.focus_set()

	def back(self):           # resets the timer and returns to the main menu
		self.timing = False
		self.timestr.set("00:00")
		self.app.showPage(MainMenu)

	def restartButton(self):   # resets the timer and creates a fresh minerunner object for the current level
		self.resetTimer()
		self.paused_time = [0, 0]
		self.changeLevel(self.currentLvl)

	def pauseButton(self):      # pauses/unpauses the timer
		if self.timing:
			self.timing = False
			self.paused_time = self.getCurrentTime()
			self.minerunner.pause()
			self.paused_text.place(x=width//2, y=180, anchor="n")
		elif not self.minerunner.game_over:
			self.timing = True
			self.minerunner.unpause()
			self.startTimer()
			self.paused_text.place_forget()

	def startTimer(self):       # saves the current start time and begins the timer
		self.starttime = time.time()
		self.timing = True
		self.time()

	def stopTimer(self):        # stops the timer and returns the time it was when stopped
		self.timing = False
		return self.getCurrentTime()

	def resetTimer(self):       # stops the timer and resets it to deafult value
		self.timing = False
		self.cpause = False
		self.cheat_time = 0
		self.timestr.set("00:00")
		self.update_idletasks()

	def time(self):          # updates the timer text and calls itself until stopped
		if self.timing:
			minutes, seconds = self.getCurrentTimeInt()
			self.timestr.set(f"{str(minutes).zfill(2)}:{str(seconds).zfill(2)}")
			window.after(100, self.time)

	def getCurrentTime(self):    # returns the current time in minutes and seconds
		timedelta = time.time() - self.starttime
		seconds = float(timedelta)
		minutes = seconds // 60
		seconds -= minutes * 60
		return minutes+self.paused_time[0], seconds+self.paused_time[1]

	def getCurrentTimeInt(self):     # returns the current time wiht integers
		minutes, seconds = self.getCurrentTime()
		return int(minutes), int(seconds)

	def finalizeTime(self):          # returns the final time formatted to include milliseconds
		if self.cheat_time:
			return self.cheat_time
		m, s = self.stopTimer()
		s, ms = str(s).split(".")
		final_time = f"{str(int(m))}:{s.zfill(2)}.{ms[:3]}"
		return final_time

	def won(self):        # when the user wins the leaderboards, user record and labels are updated
		final_time = self.finalizeTime()
		if self.currentLvl in self.app.randomtitles:
			i = self.app.randomtitles.index(self.currentLvl)
			if self.lowerTime(final_time, self.app.randomscores[i]):
				self.app.randomscores[i] = final_time
				self.updateLeaderboard(final_time, self.currentLvl)
		elif self.lowerTime(final_time, self.app.levelprogression[self.currentLvl]):
			self.app.levelprogression[self.currentLvl] = final_time
			self.updateLeaderboard(final_time, self.currentLvl)

		self.won_text.lift(self.minerunner)
		self.time_text.lift(self.minerunner)
		self.retry_button.lift(self.minerunner)
		self.nextlevel_button.lift(self.minerunner)
		self.won_text.place(x=width//2, y=180, anchor="n")
		self.timevalue.set(f" {final_time} ")
		self.time_text.place(x=width//2, y=250, anchor="n")
		self.retry_button.place(x=width//2, y=300, anchor="n")
		if isinstance(self.currentLvl, int) and self.currentLvl < 24:
			self.nextlevel_button.place(x=width//2+45, y=300, anchor="n")
			self.retry_button.place(x=width//2-65, y=300, anchor="n")

	def lost(self):      # when the user loses labels and restart button are added
		self.finalizeTime()
		self.lost_text.place(x=width//2, y=200, anchor="n")
		self.retry_button.place(x=width//2, y=260, anchor="n")
		self.lost_text.lift(self.minerunner)
		self.retry_button.lift(self.minerunner)

	def lowerTime(self, new, old):   # returns true if first formatted time is shorter than the second formatted time
		if old == "0":
			return True

		nm, ns = new.split(":")
		om, os = old.split(":")
		if nm < om:
			return True
		elif nm == om and ns < os:
			return True
		return False

	def updateLeaderboard(self, time, lvl):      # updates the leaderboard file for the current level
		csvfile = f"leaderboards/level{lvl}.csv"
		with open(csvfile, newline="") as f:
			lboard = []
			for row in csv.reader(f):
				lboard.append(row)

		name = self.app.username.get()
		for i in range(len(lboard)):
			if name == lboard[i][1] and self.lowerTime(lboard[i][0], time):
				break
			if self.lowerTime(time, lboard[i][0]):
				for j in range(i, len(lboard)-1):
					if lboard[j][1] == name:
						del lboard[j]
				lboard.insert(i, [time, name])
				break
		else:
			lboard.append([time, name])
		with open(csvfile, "w", newline="") as f:
			writer = csv.writer(f)
			for row in lboard:
				writer.writerow(row)

	def forgetTopText(self):              # removes all labels that may have been placed above the game canvas
		self.paused_text.place_forget()
		self.won_text.place_forget()
		self.lost_text.place_forget()
		self.time_text.place_forget()
		self.nextlevel_button.place_forget()
		self.retry_button.place_forget()

	def nextLevel(self):              # changes to the next level
		self.changeLevel(self.currentLvl+1)

	def cheatPause(self, *e):         # pauses the game but allows the user to continue moving
		self.timing = False
		self.cpause = True
		self.cheat_time = self.finalizeTime()

# A simple page only displaying an excel screenshot
class BossPage(tk.Frame):

	def __init__(self, app):
		tk.Frame.__init__(self, app, width=width, height=height)
		self.pack_propagate(0)
		self.app = app

		self.background_image = tk.PhotoImage(file="images/spreadsheet.png")

		canvas = tk.Canvas(self, width=width, height=height, bg="blue")
		canvas.create_image(0, 0, image=self.background_image, anchor="nw")
		canvas.pack(expand="yes", fill="both")

# A Tkinter canvas object containing a minerunner game
class minerunnerCanvas(tk.Canvas):

	def __init__(self, root, page, lvl):
		self.loadLevelData(lvl)
		tk.Canvas.__init__(self, root, width=self.width*33+1, height=self.height*33+1, bd=0, highlightthickness=0)
		self.page = page
		self.level_paused = False

		self.createImageDict()
		self.generateImageGrid()
		self.flag_grid = [""] * self.squares

		self.currentPos = [0, self.height//2]
		self.char_img = tk.PhotoImage(file="images/man.png")
		self.character = tk.Label(self, image=self.char_img, borderwidth=0)
		self.character.place(x=8, y=(self.height*33)//2-7)

		self.bind("<Up><Up><Down><Down><Left><Right><Left><Right>", self.revealBombs)
		self.bind("pause", self.cheatPause)

		self.bind("<a>", self.leftKey)
		self.bind("<d>", self.rightKey)
		self.bind("<w>", self.upKey)
		self.bind("<s>", self.downKey)
		self.bind("<Left>", self.leftKey)
		self.bind("<Right>", self.rightKey)
		self.bind("<Up>", self.upKey)
		self.bind("<Down>", self.downKey)

	def loadLevelData(self, lvl):    # loads the relevant data for a game by reading an external file
		if lvl == "Easy":
			w, h, sq, b = 19, 9, 171, 20
		elif lvl == "Medium":
			w, h, sq, b = 25, 15, 375, 60
		elif lvl == "Hard":
			w, h, sq, b = 35, 15, 525, 110
		else:
			with open(f"levels/level{str(lvl)}.txt", "r") as f:
				self.bomb_grid = []
				for row in f.read().split("\n"):
					bomb_row = row.split(", ")
					if len(bomb_row) > 1:
						self.bomb_grid.append(bomb_row)
				w = len(self.bomb_grid[0])
				h = len(self.bomb_grid)
				sq = w * h

		self.width = w
		self.height = h
		self.squares = sq
		self.game_over = False
		if lvl in ["Easy", "Medium", "Hard"]:
			self.generateBombs(b)
		else:
			self.fillAdjacentNums()

	def getCoordsFromN(self, n):    # given an index in a list, it returns the x and y locations on the grid
		y = n//self.width
		x = n - y*self.width
		return x, y

	def getNFromCoords(self, x, y):  # given x and y locations on the grid, it returns the index in a list
		n = y*self.width + x
		return n

	def pause(self):
		self.level_paused = True

	def unpause(self):
		self.level_paused = False

	def leftKey(self, e):
		self.moveTo("L")

	def rightKey(self, e):
		self.moveTo("R")

	def upKey(self, e):
		self.moveTo("U")

	def downKey(self, e):
		self.moveTo("D")

	def moveTo(self, d):
		if self.game_over or self.level_paused:
			return

		x, y = self.currentPos
		if d == "L":
			nx, ny = x-1, y
		elif d == "R":
			nx, ny = x+1, y
		elif d == "U":
			nx, ny = x, y-1
		elif d == "D":
			nx, ny = x, y+1

		if 0 <= nx < self.width and 0 <= ny < self.height:
			if self.flag_grid[self.getNFromCoords(nx, ny)] != "F":
				self.currentPos = [nx, ny]
				self.character.place(x=nx*33+8, y=ny*33+9)
				if nx == self.width-1:
					self.win()
				else:
					self.revealSquare(self.getNFromCoords(nx, ny))

	def createImageDict(self):     # creates a dictionary of images used in the game
		base_image = tk.PhotoImage(file="images/base.png")
		finish_image = tk.PhotoImage(file="images/finish.png")
		flag_image = tk.PhotoImage(file="images/flag.png")
		falseflag_image = tk.PhotoImage(file="images/falseflag.png")
		bomb_image = tk.PhotoImage(file="images/exploded.png")
		start_image = tk.PhotoImage(file="images/start.png")
		missed_image = tk.PhotoImage(file="images/bomb.png")
		win_image = tk.PhotoImage(file="images/winsquare.png")
		lose_image = tk.PhotoImage(file="images/losesquare.png")

		image_0 = tk.PhotoImage(file="images/clicked.png")
		image_1 = tk.PhotoImage(file="images/1.png")
		image_2 = tk.PhotoImage(file="images/2.png")
		image_3 = tk.PhotoImage(file="images/3.png")
		image_4 = tk.PhotoImage(file="images/4.png")
		image_5 = tk.PhotoImage(file="images/5.png")
		image_6 = tk.PhotoImage(file="images/6.png")
		image_7 = tk.PhotoImage(file="images/7.png")
		image_8 = tk.PhotoImage(file="images/8.png")

		self.image_dict = {0: image_0, 1: image_1, 2: image_2, 3: image_3, 4: image_4, 5: image_5, 6: image_6, 7: image_7, 8: image_8, "base": base_image, "finish": finish_image, "flag": flag_image, "fflag": falseflag_image, "bomb": bomb_image, "start": start_image, "missed": missed_image, "win": win_image, "lose": lose_image}

	def generateImageGrid(self):     # creates the grid of images used in the game
		image_grid = [None] * self.squares
		for i in range(self.squares):
			x, y = self.getCoordsFromN(i)
			if x == self.width-1:
				image_grid[i] = tk.Label(self, image=self.image_dict["finish"])
			else:
				image_grid[i] = tk.Label(self, image=self.image_dict["base"], bg="#232E49")
				image_grid[i].bind("<Button-1>", lambda e, x=i: self.remvButton(x))
				image_grid[i].bind("<Button-3>", lambda e, x=i: self.flagButton(x))
			image_grid[i].place(x=x*33, y=y*33)
		self.image_grid = image_grid
		self.image_grid[self.getNFromCoords(0, self.height//2)].configure(image=self.image_dict["start"])

	def generateBombs(self, bombs):   # generates ramdom positions for bombs, avoiding the location the player starts at
		s = self.height // 2
		avoid=[[0, s+1], [0, s], [0, s-1], [1, s+1], [1, s], [1, s-1], [2, s+1], [2, s], [2, s-1]]
		self.bomb_grid = [[""]*self.width for i in range(self.height)]
		for i in range(bombs):
			x, y = avoid[0]
			while [x, y] in avoid:
				x, y = rand.randint(0, self.width-2), rand.randint(0, self.height-1)
			self.bomb_grid[y][x] = "x"
			avoid.append([x, y])
		self.fillAdjacentNums()

	def fillAdjacentNums(self):     # fills the grid with numbers indicating the amount of bombs in adjacent squares
		for x in range(self.width):
			for y in range(self.height):
				if self.bomb_grid[y][x] == "x":
					continue
				self.bomb_grid[y][x] = len(self.checkAdjacent(x, y))

	def checkAdjacent(self, x, y, match=["x"]):    # returns a list of coordinates adjacent to given x y, that match given parameters
		match_list = []
		surr = [[x-1, y-1], [x-1, y], [x-1, y+1], [x, y-1], [x, y+1], [x+1, y-1], [x+1, y], [x+1, y+1]]
		for coord in surr:
			try:
				x, y = coord[0], coord[1]
				if self.bomb_grid[y][x] in match and x >= 0 and y >= 0:
					match_list.append([x, y])
			except IndexError:
				continue
		return match_list

	def remvButton(self, i):         # runs when the player left clicks on a square, reveals that square if its not flagged
		if self.game_over or self.level_paused:
			return
		if self.flag_grid[i] == "":
			self.revealSquare(i)

	def flagButton(self, i):         # runs when the player right clicks on a square, flags or unflags the square as needed
		if self.game_over or self.level_paused:
			return
		if self.flag_grid[i] == "":
			self.flag_grid[i] = "F"
			self.image_grid[i].configure(image=self.image_dict["flag"])
		elif self.flag_grid[i] == "F":
			self.flag_grid[i] = ""
			self.image_grid[i].configure(image=self.image_dict["base"])

	def revealSquare(self, i):       # reveals the square clicked by the user, calls lose function if square is a bomb
		if not self.page.timing and not self.page.cpause:
			self.page.startTimer()
		self.image_grid[i].unbind("<Button 1>")
		self.flag_grid[i] = "O"
		x, y = self.getCoordsFromN(i)
		b = self.bomb_grid[y][x]
		if b == "x":
			self.image_grid[i].configure(image=self.image_dict["bomb"])
			self.lose([x, y])
		else:
			self.image_grid[i].configure(image=self.image_dict[b])
			if b == 0:
				self.removeZeros(i)

	def removeZeros(self, i):       # if the user clicks a square with zero adjacent bombs, all adjacent squares are removed recursively
		x, y = self.getCoordsFromN(i)
		zeros = self.checkAdjacent(x, y, match=[n for n in range(9)])
		for z in zeros:
			new = self.getNFromCoords(z[0], z[1])
			if self.flag_grid[new] == "" and z[0] != self.width-1:
				self.revealSquare(new)

	def win(self):              # called when the user wins
		self.game_over = True

		x = self.width-1
		for y in range(self.height):
			i = self.getNFromCoords(x, y)
			self.image_grid[i] = tk.Label(self, image=self.image_dict["win"], bg="#5DD32A")
			self.image_grid[i].place(x=x*33, y=y*33)
		self.page.won()

	def lose(self, pressed):    # called when user loses, shows all bomb positions
		self.game_over = True

		self.character.place_forget()
		x = self.width-1
		for y in range(self.height):
			i = self.getNFromCoords(x, y)
			self.image_grid[i] = tk.Label(self, image=self.image_dict["lose"], bg="#232E49")
			self.image_grid[i].place(x=x*33, y=y*33)
		self.revealBombs(pressed=pressed)
		self.page.lost()

	def revealBombs(self, pressed=[100, 100], *e):     # reveals positions of bombs on the grid that arent already flagged, shows when flags are misplaced too
		for x in range(self.width):
			for y in range(self.height):
				n = self.getNFromCoords(x, y)
				if self.bomb_grid[y][x] == "x" and self.flag_grid[n] != "F" and [x, y] != pressed:
					self.image_grid[n].configure(image=self.image_dict["missed"])
				if self.flag_grid[n] == "F" and self.bomb_grid[y][x] != "x":
					self.image_grid[n].configure(image=self.image_dict["fflag"])

	def cheatPause(self, *e):     # pauses the game but allows the user to move
		self.page.cheatPause()


width, height = 1280, 720
window = App()
window.mainloop()
