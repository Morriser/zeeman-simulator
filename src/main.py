"""
Zeeman-effect visualizer, simulating a Favbry-Perot inferferometer.
Updated: 2020-12-01

Morris Eriksson, Pelle Nydahl, Oscar Wollman, Hannes Karlsson
"""

import json
import tkinter as tk
import numpy as np
import zeeman
import matplotlib.pyplot as mplplt
import matplotlib.figure as mplfig
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
import tkinter.ttk as ttk

class Variables:
	def __init__(self, B=1e1, t=3e4, f=2e6, mode="hot", size=200):

		# Physical variables
		self.B = B				# [T] Magnetic field strength
		self.t = t				# [nm] Distance between spectrometer mirrors
		self.f = f  			# [nm] Focal length  
		
		# Rendering variables
		self.mode = mode		# Rendering mode (gray, hot, or color)
		self.size = size		# Sidelength of image in pixels

class GUIApp(ttk.Frame):
	"""Main class for the GUI. Inherits tkk.Frame"""

	def __init__(self, parent):
		ttk.Frame.__init__(self, master=parent)
		self.parent = parent

		# Create lightsource and variables object
		self.source = lightSources[list(lightSources.keys())[0]]
		self.variables = Variables()

		# Menu
		self.frame_menu = Menu(self)
		self.frame_menu.config(padding="0.1i", borderwidth=1, relief=tk.RIDGE)
		self.frame_menu.pack(fill=tk.Y, side=tk.LEFT, padx = 5, pady = 5)

		# Figure
		self.frame_figure = FigureArea(self)
		self.frame_figure.config(padding="0.1i")
		self.frame_figure.pack(fill=tk.Y, side=tk.LEFT)

		# Draw self
		self.pack()


class Menu(ttk.Frame):
	"""Menu-part of the GUI. Inherits tkk.Frame"""

	def __init__(self, parent):
		ttk.Frame.__init__(self, master=parent)
		self.parent = parent

		# Dropdown menu: light source
		ttk.Label(self, text="Light source", font='TkDefaultFont 10 bold').grid(sticky="W", padx=10, pady=5)
		self.var_srcName = tk.StringVar()
		self.var_srcName.set(self.parent.source.name)
		self.var_srcWavelengths = tk.StringVar()
		self.var_srcWavelengths.set(lightSources[self.var_srcName.get()].v_0)
		self.drop_lightSource = ttk.OptionMenu(self, self.var_srcName, self.var_srcName.get(), *list(lightSources.keys()), command=lambda value: self.source_changed(value))
		self.drop_lightSource.config(width = 20)
		self.drop_lightSource.grid(sticky="W", padx = 0, pady = 5)

		ttk.Label(self, text="Principal wavelengths:").grid(sticky="W", padx = 0)
		ttk.Label(self, textvariable=self.var_srcWavelengths).grid(sticky="W", padx = 10)

		# Divider
		ttk.Separator(self, orient=tk.HORIZONTAL).grid(sticky="EW", pady=4)

		# Entry fields: physical variables
		ttk.Label(self, text="Variables", font='TkDefaultFont 10 bold').grid(sticky="W", padx=10, pady=5)
		self.var_B = tk.DoubleVar()
		self.var_t = tk.DoubleVar()
		self.var_f = tk.DoubleVar()
		self.var_B.set(self.parent.variables.B)
		self.var_t.set(self.parent.variables.t)
		self.var_f.set(self.parent.variables.f)

		ttk.Label(self, text="Magnetic field strength (T):").grid(sticky="W")
		self.ipf_varB = tk.Entry(self, textvariable=self.var_B)
		self.ipf_varB.grid(sticky="W", padx=10, pady=3)

		ttk.Label(self, text="Dist. between mirrors (nm):").grid(sticky="W")
		self.ipf_vart = tk.Entry(self, textvariable=self.var_t)
		self.ipf_vart.grid(sticky="W", padx=10, pady=3)

		ttk.Label(self, text="Focal length (nm):").grid(sticky="W")
		self.ipf_varf = tk.Entry(self, textvariable=self.var_f)
		self.ipf_varf.grid(sticky="W", padx=10, pady=3)

		# Divider
		ttk.Separator(self, orient=tk.HORIZONTAL).grid(sticky="EW", pady=4)

		# Radio buttons: rendering mode
		ttk.Label(self, text="Rendering", font='TkDefaultFont 10 bold').grid(sticky="W", padx=10, pady=5)
		self.var_renderMode = tk.StringVar()
		self.var_renderMode.set(self.parent.variables.mode)
		self.rbtn_renderModeGray  = ttk.Radiobutton(self, text="Grayscale", variable=self.var_renderMode, value="gray")
		self.rbtn_renderModeHot   = ttk.Radiobutton(self, text="Heatmap",   variable=self.var_renderMode, value="hot")
		self.rbtn_renderModeColor = ttk.Radiobutton(self, text="Color",     variable=self.var_renderMode, value="RGB")
		self.rbtn_renderModeGray.grid(sticky="W")
		self.rbtn_renderModeHot.grid(sticky="W")
		self.rbtn_renderModeColor.grid(sticky="W")

		# Entry field: size
		self.var_size = tk.DoubleVar()
		self.var_size.set(self.parent.variables.size)
		ttk.Label(self, text="Image side length (px):").grid(sticky="W")
		self.ipf_size = tk.Entry(self, textvariable=self.var_size)
		self.ipf_size.grid(sticky="W", padx=10, pady=3)

		# Render button
		self.btn_render = ttk.Button(self, text="Render", command = lambda: parent.frame_figure.update())
		self.btn_render.grid(sticky="W", pady = 10)

		# Divider
		ttk.Separator(self, orient=tk.HORIZONTAL).grid(sticky="EW", pady=4)

		# Save button
		self.btn_save = ttk.Button(self, text="Save", command = saveFileDialog)
		self.btn_save.grid(sticky="W", pady = 10)

		# Call once to update source
		self.source_changed(self.var_srcName.get())

	def update_variables(self):
		"""Updates the current configuration."""

		var = self.parent.variables
		var.B = self.var_B.get()
		var.t = self.var_t.get()
		var.f = self.var_f.get()
		var.mode = self.var_renderMode.get()
		var.size = int(self.var_size.get())
		var.title = self.parent.frame_figure.ipf_figureTitle.get()

	def source_changed(self, value):
		"""Updates the light source information."""

		self.parent.source = lightSources[self.var_srcName.get()]
		output = ""
		for value in self.parent.source.v_0:
			output += str(value) + " nm \n"
		self.var_srcWavelengths.set(output)


class FigureArea(ttk.Frame):
	"""GUI object containing the image of the interference pattern."""

	def __init__(self, parent):
		ttk.Frame.__init__(self, master=parent)
		self.parent = parent
		
		# Title
		self.ipf_figureTitle = tk.Entry(self, font='TkDefaultFont 14')
		self.ipf_figureTitle.insert(0, "Title")
		self.ipf_figureTitle.pack(pady=10)

		# Figure area
		self.figure = mplplt.figure()
		self.canvas = FigureCanvasTkAgg(self.figure, master=self)
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

	def update(self):
		"""Called when the 'render' button is pressed. Updates the image."""

		# Update variables
		menu = self.parent.frame_menu
		menu.update_variables()
		var = self.parent.variables

		# Get intensity map and axis range
		Imap, d = zeeman.generateImage(self.parent.source, var)
		axesRanges = [-d, d, -d, d]

		# Plot to figure
		if var.mode == "RGB":
			mplplt.imshow(Imap, extent=axesRanges)
		else:
			mplplt.imshow(Imap, var.mode, vmin=-1, vmax=1, extent=axesRanges) 
		mplplt.title(var.title)
		mplplt.xlabel(r"$\mu$m")
		mplplt.ylabel(r"$\mu$m")

		self.canvas.draw()


def saveFileDialog():
	"""Opens a save file dialog, allowing the user to save 
	the currently active image to a file."""

	filename = tk.filedialog.asksaveasfilename(
		initialdir="./", 
		initialfile="figure.png", 
		filetypes = (("PNG","*.png"),("all files","*.*")))

	if not filename: # Canceled by user, do nothing
		return
	else:
		mplplt.savefig(filename)

		
def init():
	"""Application entrypoint"""

	# Configurate tkinter
	tkRoot = tk.Tk()
	tkRoot.title("Zeeman-effect Simulator")
	tkRoot.resizable(False, False)
	tkRoot.iconbitmap('./static/icon.ico')
	tkRoot.geometry("800x600")	

	# Load light source data
	global lightSources
	lightSources = {}
	with open("./sources.json") as file:
		data = json.load(file)
		for key, value in data.items():
			lightSources[key] = zeeman.LightSource(key, value['L'], value['v_0'], value['dspin'])

	# Add exit protocol
	tkRoot.protocol("WM_DELETE_WINDOW", lambda: tkRoot.destroy())

	# Run tkinter
	GUIApp(tkRoot)
	tkRoot.mainloop()


init()