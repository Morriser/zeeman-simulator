'''
    == A few notes about color ==

    Color   Wavelength(nm) Frequency(THz)
    Red     620-750        484-400
    Orange  590-620        508-484
    Yellow  570-590        526-508
    Green   495-570        606-526
    Blue    450-495        668-606
    Violet  380-450        789-668

    Based on code by Dan Bruton
    http://www.physics.sfasu.edu/astro/color/spectra.html

'''

def waveToRGB(w):
    """ Converts a given wavelength 'w' of light to an approximate RGB color 
        value. The w must be given in nanometers in the range from 
        380 nm through 750 nm. Returns a list of integer values between 0 and 
        256 in the form [R, G, B]. """

    w = float(w)

    if w >= 380 and w <= 440:
        attenuation = 0.3 + 0.7 * (w - 380) / (440 - 380)
        R = (-(w - 440) / (440 - 380)) * attenuation
        G = 0.0
        B = (1.0 * attenuation)

    elif w >= 440 and w <= 490:
        R = 0.0
        G = (w - 440) / (490 - 440)
        B = 1.0

    elif w >= 490 and w <= 510:
        R = 0.0
        G = 1.0
        B = -(w - 510) / (510 - 490)

    elif w >= 510 and w <= 580:
        R = (w - 510) / (580 - 510)
        G = 1.0
        B = 0.0

    elif w >= 580 and w <= 645:
        R = 1.0
        G = -(w - 645) / (645 - 580)
        B = 0.0

    elif w >= 645 and w <= 750:
        attenuation = 0.3 + 0.7 * (750 - w) / (750 - 645)
        R = 1.0 * attenuation
        G = 0.0
        B = 0.0

    else:
        R = 0.0
        G = 0.0
        B = 0.0

    R *= 255; G *= 255; B *= 255
    return [int(R), int(G), int(B)]