"""
Zeeman-effect visualizer, simulating a Favbry-Perot inferferometer.
Updated: 2020-12-01

Morris Eriksson, Pelle Nydahl, Oscar Wollman, Hannes Karlsson
"""

import math

# Math definitions
cos = math.cos
sin = math.sin
pi = math.pi

# Physical constants 
e     = 1.60217662e-19    # [kg]  Charge of the electron
m     = 9.10938356e-31    # [kg]  Mass of the electron
c     = 299792458         # [m/s] Speed of light
h     = 6.626e-34         # [J*s] Planck's constant
mu_B  = 9.2740099e-24     # [J/T] Bohr magneton
s     = 1/2               # Electron spin


def energyShift(source, varbs):
	"""Finds the energy shift caused by the magnetic field by calculating 
	the quantum numbers m_j. Outputs the energy shifts as a list."""

	dE = []
	l_1 = source.L[0]
	l_2 = source.L[1]

	for m_l in range(-(l_1-l_2),(l_1-l_2+1)):
		for m_s in source.dspin:
			m_j = m_l + m_s
			dE.append(mu_B * m_j * varbs.B)
	
	return dE


def findWavelengths(source, dE):
	"""Uses the energy shifts and the base wavelength(s) to calculate the 
	wavelength shifts, and outputs a list with every wavelength."""

	v = []                   			# List of wavelengths
	v_0 = source.v_0

	if type(v_0) == int or type(v_0) == float:
		origE = h*c/(v_0*1e-9)   		# Base energy level

		for elem in dE:
			E = origE + elem
			v.append((h*c/E)*1e+9)

	elif type(v_0) == list:
		origE = []
		for w in v_0:
			origE.append(h*c/(w*1e-9)) 	# Base energy levels

		for E_0 in origE:
			for elem in dE:
				E = E_0 + elem
				v.append((h*c/E)*1e+9)

	return v

  
def intensity(w, radius, varbs):
	"""Returns the light intensity L (between 0 and 1) as a function of r, 
	where r specifices the radius."""
  
	n = 1                           # Refractive index of air
	k = 2*pi / w    				# Wave number
	
	theta = radius / varbs.f             
	Fin = 100						# Sharpness of the interference pattern
	delta2 = k * n * varbs.t * cos(theta)
	I = 1 / (1 + Fin*sin(delta2)**2)

	return I


def generateImage(source, varbs):
	"""Generates an interference pattern image of the wavelengths in v. 
	'size' is the width and height of the image. 
	'mode' is the matplotlib drawing mode (heatmap by default) """

	from wave_to_rgb import waveToRGB

	# Calculate wavelengths
	dE = energyShift(source, varbs)
	wavelengths = findWavelengths(source, dE)

	mode = varbs.mode
	size = varbs.size

	# Create intensity map
	if mode == "RGB":
		I = [[[0, 0, 0] for i in range(size)] for j in range(size)]
	else:
		I = [[0 for i in range(size)] for j in range(size)]

	for w in wavelengths:
		for x in range(size):
			for y in range(size):

				# Define physical step length per pixel
				step = 5000   # [nm]

				# Transform from pixel space to physical space
				X = (x - size/2) * step
				Y = (y - size/2) * step
				R = math.sqrt(X**2 + Y**2)

				# Calculate interference through superposition
				if mode == "RGB":
					RGB = waveToRGB(w)
					for i in range(3):
						I[x][y][i] += int(intensity(w, R, varbs)*RGB[i]*1.5/len(wavelengths))

				else:
					I[x][y] += (intensity(w, R, varbs) * 2 - 1)/len(wavelengths)

	# Calculate nm intervals to plot on axes
	axisRange = (size/2 * step)	/ 1e3		# Physical distance on axes (um)
	return I, axisRange

class LightSource:
	def __init__(self, name, L, v_0, dspin):
		self.name = name		# Atomic name
		self.L = L				# Azimuthal quantum number transition
		self.v_0 = v_0			# Principal wavelengths
		self.dspin = dspin		# Spin transitions