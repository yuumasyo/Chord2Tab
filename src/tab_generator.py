# Code to Tab Generator
# Maps chord names to guitar tab positions (fingerings)

# Frets: -1 = Mute (X), 0 = Open string, 1+ = Fret number
# String index: 0=e(1st), 1=B, 2=G, 3=D, 4=A, 5=E(6th)

CHORD_SHAPES = {
    # Open Chords (Standard)
    'C': [0, 1, 0, 2, 3, -1],
    'Cm': [3, 4, 5, 5, 3, -1], # Barre chord (Root 5)
    'C#': [4, 6, 6, 6, 4, -1],
    'Db': [4, 6, 6, 6, 4, -1],
    'C#m': [4, 5, 6, 6, 4, -1],
    'Dbm': [4, 5, 6, 6, 4, -1],
    
    'D': [2, 3, 2, 0, -1, -1],
    'Dm': [1, 3, 2, 0, -1, -1],
    'D#': [3, 4, 3, 1, -1, -1],
    'Eb': [3, 4, 3, 1, -1, -1],
    'D#m': [6, 7, 8, 8, 6, -1],
    'Ebm': [6, 7, 8, 8, 6, -1],

    'E': [0, 0, 1, 2, 2, 0],
    'Em': [0, 0, 0, 2, 2, 0],
    'F': [1, 1, 2, 3, 3, 1], # Barre chord (Root 6)
    'Fm': [1, 1, 1, 3, 3, 1],
    'F#': [2, 2, 3, 4, 4, 2],
    'Gb': [2, 2, 3, 4, 4, 2],
    'F#m': [2, 2, 2, 4, 4, 2],
    'Gbm': [2, 2, 2, 4, 4, 2],

    'G': [3, 0, 0, 0, 2, 3],
    'Gm': [3, 3, 3, 5, 5, 3], # Barre chord (Root 6)
    'G#': [4, 4, 5, 6, 6, 4],
    'Ab': [4, 4, 5, 6, 6, 4],
    'G#m': [4, 4, 4, 6, 6, 4],
    'Abm': [4, 4, 4, 6, 6, 4],

    'A': [0, 2, 2, 2, 0, -1],
    'Am': [0, 1, 2, 2, 0, -1],
    'A#': [1, 3, 3, 3, 1, -1], # Barre chord (Root 5)
    'Bb': [1, 3, 3, 3, 1, -1],
    'A#m': [1, 2, 3, 3, 1, -1],
    'Bbm': [1, 2, 3, 3, 1, -1],

    'B': [2, 4, 4, 4, 2, -1],
    'Bm': [2, 3, 4, 4, 2, -1],
}

# Root Note Positions for Power Chords
# Maps Root Note -> (String Index (0-5), Fret)
# 5 = E string (Low), 4 = A string, 3 = D string
ROOT_POSITIONS = {
    'E': (5, 0), 'F': (5, 1), 'F#': (5, 2), 'Gb': (5, 2), 'G': (5, 3), 'G#': (5, 4), 
    'Ab': (5, 4), 'A': (5, 5), 'A#': (5, 6), 'Bb': (5, 6), 'B': (5, 7),
    
    'C': (4, 3), 'C#': (4, 4), 'Db': (4, 4), 'D': (4, 5), 'D#': (4, 6), 'Eb': (4, 6),
}

NOTE_TO_SEMITONE = {
    'C': 0, 'C#': 1, 'Db': 1,
    'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10,
    'B': 11,
}

# String index (0=e ... 5=E) -> open note semitone
OPEN_STRING_SEMITONE = {
    5: 4,   # Low E
    4: 9,   # A
    3: 2,   # D
}


def _is_minor_chord(chord_name):
    return 'm' in chord_name and 'maj' not in chord_name


def _dedupe_fingerings(fingerings):
    unique = []
    seen = set()
    for fingering in fingerings:
        key = tuple(fingering)
        if key in seen:
            continue
        seen.add(key)
        unique.append(list(fingering))
    return unique


def _position_key(fingering):
    frets = [f for f in fingering if f >= 0]
    if not frets:
        return (999, 999, 999)
    span = max(frets) - min(frets)
    avg = sum(frets) / len(frets)
    return (min(frets), span, avg)


def _in_playable_range(fingering, max_fret=15):
    frets = [f for f in fingering if f >= 0]
    return bool(frets) and max(frets) <= max_fret


def _build_root6_shape(root_fret, is_minor):
    if is_minor:
        # Fm form: [1,1,1,3,3,1]
        return [root_fret, root_fret, root_fret, root_fret + 2, root_fret + 2, root_fret]
    # F form: [1,1,2,3,3,1]
    return [root_fret, root_fret, root_fret + 1, root_fret + 2, root_fret + 2, root_fret]


def _build_root5_shape(root_fret, is_minor):
    if is_minor:
        # Bbm form: [1,2,3,3,1,-1]
        return [root_fret, root_fret + 1, root_fret + 2, root_fret + 2, root_fret, -1]
    # Bb form: [1,3,3,3,1,-1]
    return [root_fret, root_fret + 2, root_fret + 2, root_fret + 2, root_fret, -1]

def get_root_from_name(chord_name):
    if not chord_name: return 'C'
    if len(chord_name) > 1 and chord_name[1] in ['#', 'b']:
        return chord_name[:2]
    return chord_name[:1]

def get_power_chord(chord_name):
    """
    Generate power chord fingering
    """
    root = get_root_from_name(chord_name)
    
    # Custom adjustments for better playability
    if root == 'A': pos = (4, 0) # Open A prefer open string over 5th fret E string
    elif root == 'D': pos = (3, 0) # Open D
    elif root == 'B': pos = (4, 2)
    elif root == 'Bb': pos = (4, 1)
    elif root == 'A#': pos = (4, 1)
    else:
        pos = ROOT_POSITIONS.get(root)
    
    if not pos:
        # Fallback to E (lowest) if unknown
        pos = (5, 0)

    root_string_idx, fret = pos
    fingering = [-1] * 6
    
    # Root
    fingering[root_string_idx] = fret
    
    # 5th (one string higher = index - 1)
    fifth_string = root_string_idx - 1
    if fifth_string >= 0:
        fingering[fifth_string] = fret + 2
    
    # Octave (two strings higher = index - 2)
    octave_string = root_string_idx - 2
    if octave_string >= 0:
        fingering[octave_string] = fret + 2
        
    return fingering


def _get_basic_chord_fingering(chord_name):
    if not chord_name:
        return [-1] * 6

    if chord_name in CHORD_SHAPES:
        return CHORD_SHAPES[chord_name]

    root = get_root_from_name(chord_name)
    is_minor = _is_minor_chord(chord_name)
    base_name = root + ('m' if is_minor else '')

    if base_name in CHORD_SHAPES:
        return CHORD_SHAPES[base_name]

    if root in CHORD_SHAPES:
        return CHORD_SHAPES[root]

    return [-1] * 6


def get_chord_fingering_options(chord_name, mode='standard'):
    """
    Returns same-chord fingering candidates sorted from low to high position.
    """
    if not chord_name:
        return [[-1] * 6]

    root = get_root_from_name(chord_name)
    root_semitone = NOTE_TO_SEMITONE.get(root)

    if mode == 'power':
        if root_semitone is None:
            return [get_power_chord(chord_name)]

        options = []
        for root_string_idx in [5, 4, 3]:
            open_semitone = OPEN_STRING_SEMITONE[root_string_idx]
            base_fret = (root_semitone - open_semitone) % 12

            for octave in [0, 12]:
                fret = base_fret + octave
                fingering = [-1] * 6
                fingering[root_string_idx] = fret

                fifth_string = root_string_idx - 1
                octave_string = root_string_idx - 2
                if fifth_string >= 0:
                    fingering[fifth_string] = fret + 2
                if octave_string >= 0:
                    fingering[octave_string] = fret + 2

                if _in_playable_range(fingering):
                    options.append(fingering)

        options = _dedupe_fingerings(options)
        options.sort(key=_position_key)
        return options or [get_power_chord(chord_name)]

    options = []

    # Open / custom dictionary form first so reset returns the familiar shape.
    basic = _get_basic_chord_fingering(chord_name)
    if basic != [-1] * 6:
        options.append(basic)

    if root_semitone is not None:
        is_minor = _is_minor_chord(chord_name)

        # Root on low E string (F/Fm shape)
        base_fret_e = (root_semitone - OPEN_STRING_SEMITONE[5]) % 12
        for octave in [0, 12]:
            root_fret = base_fret_e + octave
            fingering = _build_root6_shape(root_fret, is_minor)
            if _in_playable_range(fingering):
                options.append(fingering)

        # Root on A string (Bb/Bbm shape)
        base_fret_a = (root_semitone - OPEN_STRING_SEMITONE[4]) % 12
        for octave in [0, 12]:
            root_fret = base_fret_a + octave
            fingering = _build_root5_shape(root_fret, is_minor)
            if _in_playable_range(fingering):
                options.append(fingering)

    options = _dedupe_fingerings(options)
    options.sort(key=_position_key)
    return options or [[-1] * 6]

def get_chord_fingering(chord_name, mode='standard'):
    """
    Returns a list of 6 integers representing fret numbers from high e (0) to low E (5).
    -1 means mute.
    """
    options = get_chord_fingering_options(chord_name, mode=mode)
    return options[0] if options else [-1] * 6

def format_tab_string(fingering):
    """
    Formats a single chord fingering into a vertical stack string for display
    """
    lines = []
    string_names = ['e', 'B', 'G', 'D', 'A', 'E']
    
    for i, fret in enumerate(fingering):
        fret_char = str(fret) if fret != -1 else 'x'
        lines.append(f"{string_names[i]} |-{fret_char}-|")
        
    return "\n".join(lines)

def generate_ascii_tab(chords_data, mode='standard'):
    """
    Generates a full ASCII tab for the song.
    chords_data: List of dicts {'chord': 'Am', 'duration': ..., 'start': ...}
    """
    # Create 6 lines for strings
    # 0=e, 1=B, 2=G, 3=D, 4=A, 5=E
    string_labels = ["e", "B", "G", "D", "A", "E"]
    tab_lines = {i: f"{string_labels[i]} |" for i in range(6)}
    
    for segment in chords_data:
        chord = segment['chord']
        fingering = get_chord_fingering(chord, mode)
        
        # Determine cell width based on duration or just readable width
        # For simplicity, fixed width per chord change
        width = max(len(chord) + 2, 6)
        
        # Add Chord Name above the tab? (Not handled in this simple ASCII generator, 
        # but usually you'd want the chord name displayed separately or above)
        
        for i in range(6):
            fret = fingering[i]
            fret_str = str(fret) if fret != -1 else '-'
            # Center the fret number
            cell = f"{fret_str}".center(width, '-')
            tab_lines[i] += cell + "|"
            
    # Combine lines
    return "\n".join([tab_lines[i] for i in range(6)])
