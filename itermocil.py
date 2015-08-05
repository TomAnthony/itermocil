import subprocess
import yaml

from math import ceil


class itermocil(object):
    """ Read the teamocil file and build an Applescript that will configure
        iTerm into the correct layout. Uses an Applescript to establish
        which version of iTerm is being used and supplies different 
        Applescript based upon that.
    """

    def __init__(self, teamocil_file, here=False):
        """ Establish iTerm version, and initialise the list which
            will contain all the Applescript commands to execute.
        """

        # Check whether we are old or new iTerm (pre/post 2.9)
        major_version = self.get_major_version()
        self.new_iterm = True
        if major_version < 2.9:
            self.new_iterm = False

        # Initiate from arguments
        self.file = teamocil_file
        self.here = here

        # This will be where we build up the script.
        self.applescript = []
        self.applescript.append('tell application "iTerm"')
        self.applescript.append('activate')

        # If we need to open a new window, then add necessary commands
        # to script.
        if not self.here:
            if self.new_iterm:
                self.applescript.append('create window with default profile')
            else:
                self.applescript.append('tell i term application "System Events" ' +
                                        'to keystroke "n" using command down')

        # Process the file, building the script.
        self.process_file()

        # Finish the script
        self.applescript.append('end tell')

    def get_major_version(self):
        """ Get version of iTerm. 'iTerm2' (iTerm 2.9+) has much improved
            Applescript support and options, so is more robust.
        """

        osa = subprocess.Popen(['osascript', '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)

        version_script = 'set iterm_version to (get version of application "iTerm")'
        v = osa.communicate(version_script)[0]

        return float(v[:3])

    def execute(self):
        """ Execute the Applescript built by parsing the teamocil file.
        """

        parsed_script = "\n".join(self.applescript)

        osa = subprocess.Popen(['osascript', '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)

        return osa.communicate(parsed_script)[0]

    def script(self):
        """ Return the Applescript we have built (so far). Mainly for
            debugging purposes.
        """

        parsed_script = "\n".join(self.applescript)

        return parsed_script

    def arrange_panes(self, num_panes, layout="tiled"):
        """ Create a set of Applescript instructions to generate the desired
            layout of panes. Attempt to match teamocil layout behaviour as
            closely as is possible.

            See 'arrange_panes_old_iterm' for an alternate version for
            generating a version for old iTerm.
        """

        def create_pane(parent, child, split="vertical"):

            return (''' tell pane_{pp}
                            set pane_{cp} to (split {o}ly with same profile)
                        end tell
                    '''.format(pp=parent, cp=child, o=split))

        # Link a variable to the current window.
        self.applescript.append("set pane_1 to (current session of current window)")

        # teamocil seems to treat the first 2 tiles of a tiled layout like this
        if num_panes == 2:
            if layout == 'tiled':
                layout = 'even-vertical'

        # 'even-horizontal' layouts just split vertically across the screen
        if layout == 'even-horizontal':

            for p in range(2, num_panes+1):
                self.applescript.append(create_pane(p-1, p, "vertical"))

        # 'even-vertical' layouts just split horizontally down the screen
        if layout == 'even-vertical':

            for p in range(2, num_panes+1):
                self.applescript.append(create_pane(p-1, p, "horizontal"))

        # 'main-vertical' layouts have one left pane  that is full height,
        # and then split the remaining panes horizontally down the right
        elif layout == 'main-vertical':

            self.applescript.append(create_pane(1, 2, "vertical"))
            if num_panes > 1:
                for p in range(3, num_panes+1):
                    self.applescript.append(create_pane(p-1, p, "horizontal"))

        # 'tiled' layouts create 2 columns and then however many rows as
        # needed. If there are odd number of panes then the bottom pane
        # spans two columns. Panes are numbered top to bottom, left to right.
        elif layout == 'tiled':

            vertical_splits = int(ceil((num_panes / 2.0))) - 1
            second_columns = num_panes / 2

            for p in range(0, vertical_splits):
                pp = (p * 2) + 1
                cp = pp + 2
                self.applescript.append(create_pane(pp, cp, "horizontal"))

            for p in range(0, second_columns):
                pp = (p * 2) + 1
                cp = pp + 1
                self.applescript.append(create_pane(pp, cp, "vertical"))

        # Raise an exception if we don't recognise the layout setting.
        else:
            raise ValueError("Unknown layout setting.")

    def arrange_panes_old_iterm(self, num_panes, layout="tiled"):
        """ Create a set of Applescript instructions to generate the desired
            layout of panes. Attempt to match teamocil layout behaviour as
            closely as is possible.

            See 'arrange_panes' for the main version used for generating
            the script for the newer iTerm.
        """

        prefix = 'tell i term application "System Events" to '

        # teamocil seems to treat the first 2 tiles of a tiled layout like this
        if num_panes == 2:
            if layout == 'tiled':
                layout = 'even-vertical'

        # 'even-horizontal' layouts just split vertically across the screen
        if layout == 'even-horizontal':

            for p in range(2, num_panes+1):
                self.applescript.append(prefix + 'keystroke "d" using command down')

            # Focus back on the first pane
            self.applescript.append(prefix + 'keystroke "]" using command down')

        # 'even-vertical' layouts just split horizontally down the screen
        if layout == 'even-vertical':

            for p in range(2, num_panes+1):
                self.applescript.append(prefix + 'keystroke "D" using command down')

            # Focus back on the first pane
            self.applescript.append(prefix + 'keystroke "]" using command down')

        # 'main-vertical' layouts have one left pane  that is full height,
        # and then split the remaining panes horizontally down the right
        elif layout == 'main-vertical':

            self.applescript.append(prefix + 'keystroke "d" using command down')
            if num_panes > 1:
                for p in range(3, num_panes+1):
                    self.applescript.append(prefix + 'keystroke "D" using command down')

            # Focus back on the first pane
            self.applescript.append(prefix + 'keystroke "]" using command down')

        # 'tiled' layouts create 2 columns and then however many rows as
        # needed. If there are odd number of panes then the bottom pane
        # spans two columns. Panes are numbered top to bottom, left to right.
        elif layout == 'tiled':

            vertical_splits = int(ceil((num_panes / 2.0))) - 1
            second_columns = num_panes / 2

            for p in range(0, vertical_splits):
                self.applescript.append(prefix + 'keystroke "D" using command down')

            if vertical_splits > 0:
                # If we split vertically at all then move 'down' a pane to take
                # us back to the initial pane.
                self.applescript.append(prefix + 'key code 125 using {command down, option down}')

            for p in range(0, second_columns):
                self.applescript.append(prefix + 'keystroke "d" using command down')
                self.applescript.append(prefix + 'keystroke "]" using command down')

            if num_panes % 2 != 0:
                # If odd number of panes then move once more to return to initial pane.
                self.applescript.append(prefix + 'keystroke "]" using command down')

        # Raise an exception if we don't recognise the layout setting.
        else:
            raise ValueError("Unknown layout setting.")

        # This is all keystroke based and thus takes a moment to happen,
        # so unfortunately (for old iTerm) we have to wait a moment to
        # give all that time to happen.
        self.applescript.append('delay 3')

    def initiate_pane(self, pane, commands="", name=None):
        """ Once we have layed out the panes we need, we can now navigate
            to the specified starting directory and run the specified
            commands for each pane.
        """

        # Old iTerm requirs referencing panes in this format!
        nth = {
             1: "first",       2: "second",       3: "third",
             4: "fourth",      5: "fifth",        6: "sixth",
             7: "seventh",     8: "eighth",       9: "ninth",
            10: "tenth",      11: "eleventh",    12: "twelth",
            13: "thirteenth", 14: "fourteenth",  15: "fifteenth",
            16: "sixteenth",  17: "seventeenth", 18: "eighteenth",
            19: "nineteenth", 20: "twentieth",   21: "twentyfirst"
        }

        # Determine the correct target for Applescript's 'tell' command
        # based upon iTerm version.
        if self.new_iterm:
            tell_target = 'pane_%s' % pane
        else:
            tell_target = nth[pane] + ' session of current terminal'

        # Setting the pane name is mercifully the same across both
        # iTerm versions.
        if name:
            name_command = 'set name to "' + name + '"'

        # Turn commands list into a string command
        command = "; ".join(commands)

        # Build the applescript snippet.
        self.applescript.append(
            ''' tell {tell_target}
                    write text "{command}"
                    {name}
                end tell
            '''.format(tell_target=tell_target, command=command, name=name_command))

    def process_file(self):
        """ Parse the named teamocil file, generate Applescript to send to
            iTerm2 to generate panes, name them and run the specified commands
            in them.
        """

        # Open up the file and parse it with PyYaml
        with open(self.file, 'r') as f:
            teamocil_config = yaml.load(f)

        for num, window in enumerate(teamocil_config['windows']):
            if num > 0:
                self.applescript.append("create window with default profile")
            base_command = []

            # Extract layout format, if given.
            if "layout" in window:
                layout = window['layout']
            else:
                layout = "tiled"

            # Extract starting directory for panes in this window, if given.
            if 'root' in window:
                base_command.append('cd {path}'.format(path=window['root']))

            # Generate Applescript to lay the panes out and then add to our
            # Applescript commands to run.
            if self.new_iterm:
                self.arrange_panes(len(window['panes']), layout)
            else:
                self.arrange_panes_old_iterm(len(window['panes']), layout)

            if 'panes' in window:

                for pane_num, pane in enumerate(window['panes'], start=1):
                    # each pane needs the base_command to navigate to
                    # the correct directory
                    pane_commands = []
                    pane_commands.extend(base_command)

                    # pane entries may be lists of multiple commands
                    if isinstance(pane, dict):
                        if 'commands' in pane:
                            for command in pane['commands']:
                                pane_commands.append(command)
                    else:
                        pane_commands.append(pane)

                    # Check if windoww has a name.
                    window_name = None
                    if 'name' in window:
                        window_name = window['name']

                    self.initiate_pane(pane_num, pane_commands, window_name)
