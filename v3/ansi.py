class ANSI(object):
    ''' 
    A class to print text to the terminal with ANSI styles and colors.
    Credit: <https://tinyurl.com/stackoverflow-ansi-help>
    '''

    #  Reset 
    RESET = '\033[0m'

    #  Regular Colors 
    BLACK = '\033[0;30m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'

    #  Bolded Colors 
    BLACK_BOLD = '\033[1;30m'
    RED_BOLD = '\033[1;31m'
    GREEN_BOLD = '\033[1;32m'
    YELLOW_BOLD = '\033[1;33m'
    BLUE_BOLD = '\033[1;34m'
    PURPLE_BOLD = '\033[1;35m'
    CYAN_BOLD = '\033[1;36m'
    WHITE_BOLD = '\033[1;37m'

    #  Underlined Colors 
    BLACK_UNDERLINED = '\033[4;30m'
    RED_UNDERLINED = '\033[4;31m'
    GREEN_UNDERLINED = '\033[4;32m'
    YELLOW_UNDERLINED = '\033[4;33m'
    BLUE_UNDERLINED = '\033[4;34m'
    PURPLE_UNDERLINED = '\033[4;35m'
    CYAN_UNDERLINED = '\033[4;36m'
    WHITE_UNDERLINED = '\033[4;37m'

    #  Background Colors 
    BLACK_BACKGROUND = '\033[40m'
    RED_BACKGROUND = '\033[41m'
    GREEN_BACKGROUND = '\033[42m'
    YELLOW_BACKGROUND = '\033[43m'
    BLUE_BACKGROUND = '\033[44m'
    PURPLE_BACKGROUND = '\033[45m'
    CYAN_BACKGROUND = '\033[46m'
    WHITE_BACKGROUND = '\033[47m'

    #  Bright Colors 
    BRIGHT = '\033[0;90m'
    BRIGHT_RED = '\033[0;91m'
    BRIGHT_GREEN = '\033[0;92m'
    BRIGHT_YELLOW = '\033[0;93m'
    BRIGHT_BLUE = '\033[0;94m'
    BRIGHT_PURPLE = '\033[0;95m'
    BRIGHT_CYAN = '\033[0;96m'
    BRIGHT_WHITE = '\033[0;97m'

    #  Bolded Bright Colors 
    BRIGHT_BLACK_BOLD = '\033[1;90m'
    BRIGHT_RED_BOLD = '\033[1;91m'
    BRIGHT_GREEN_BOLD = '\033[1;92m'
    BRIGHT_YELLOW_BOLD = '\033[1;93m'
    BRIGHT_BLUE_BOLD = '\033[1;94m'
    BRIGHT_PURPLE_BOLD = '\033[1;95m'
    BRIGHT_CYAN_BOLD = '\033[1;96m'
    BRIGHT_WHITE_BOLD = '\033[1;97m'

    #  Background Bright Colors 
    BRIGHT_BLACK_BACKGROUND = '\033[0;100m'
    BRIGHT_RED_BACKGROUND = '\033[0;101m'
    BRIGHT_GREEN_BACKGROUND = '\033[0;102m'
    BRIGHT_YELLOW_BACKGROUND = '\033[0;103m'
    BRIGHT_BLUE_BACKGROUND = '\033[0;104m'
    BRIGHT_PURPLE_BACKGROUND = '\033[0;105m'
    BRIGHT_CYAN_BACKGROUND = '\033[0;106m'
    BRIGHT_WHITE_BACKGROUND = '\033[0;107m'
    