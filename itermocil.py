#!/usr/bin/python

import argparse
import os
import re
import subprocess
import sys
import yaml

from math import ceil


__version__ = '0.2.1'


class Itermocil(object):
    """ Read the teamocil file and build an Applescript that will configure
        iTerm into the correct layout. Uses an Applescript to establish
        which version of iTerm is being used and supplies different
        Applescript based upon that.
    """

    def __init__(self, teamocil_file, here=False, cwd=None):
        """ Establish iTerm version, and initialise the list which
            will contain all the Applescript commands to execute.
        """

        # Check whether we are old or new iTerm (pre/post 2.9)
        major_version = self.get_major_version()
        self.new_iterm = True

        if tuple(int(n) for n in str(major_version).split(".")) < (2, 9):
            self.new_iterm = False
        else:
            # Temporary check to check for unsupported version of iTerm beta
            v = self.get_version_string()
            bits = v.split('.')
            if len(bits) > 2 and '-nightly' in str(major_version):
                build = bits[2].replace('-nightly', '')
                if (int(build) < 20150805):
                    print "This is an unsupported beta build of iTerm."
                    print "Try the latest nightly, or the 2.1.1 stable build."
                    print "See Readme notes for more info. Sorry!"
                    sys.exit(1)

        # Initiate from arguments
        self.file = teamocil_file
        self.here = here
        self.cwd = cwd

        # Open up the file and parse it with PyYaml
        with open(self.file, 'r') as f:
            self.parsed_config = yaml.load(f)

        # This will be where we build up the script.
        self.applescript = []
        self.applescript.append('tell application "iTerm"')
        self.applescript.append('activate')

        if 'pre' in self.parsed_config:
            self.applescript.append('do shell script "' + self.parsed_config['pre'] + ';"')

        # If we need to open a new window, then add necessary commands
        # to script.
        if not self.here:
            if self.new_iterm:
                self.applescript.append('tell current window')
                self.applescript.append('create tab with default profile')
                self.applescript.append('end tell')
                # self.applescript.append('create window with default profile')
            else:
                self.applescript.append('delay 0.3')
                self.applescript.append('tell i term application "System Events" ' +
                                        'to keystroke "t" using command down')
                self.applescript.append('delay 0.3')

        # Process the file, building the script.
        self.process_file()

        # Finish the script
        self.applescript.append('end tell')

    def get_version_string(self):
        """ Get version of iTerm. 'iTerm2' (iTerm 2.9+) has much improved
            Applescript support and options, so is more robust.
        """

        osa = subprocess.Popen(['osascript', '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)

        version_script = 'set iterm_version to (get version of application "iTerm")'
        v = osa.communicate(version_script)[0]

        return v.strip()

    def get_major_version(self):
        """ Get version of iTerm. 'iTerm2' (iTerm 2.9+) has much improved
            Applescript support and options, so is more robust.
        """

        v = self.get_version_string()

        try:
            mv = float(v[:3])
            return mv
        except ValueError:
            return 99.0

    def get_num_panes_in_current_window(self):
        """ Get the number of panes already existing in the current window.
            This is used only for old iTerm.
        """

        osa = subprocess.Popen(['osascript', '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)

        panes_script = """ tell application "iTerm"
                               count sessions of current terminal
                           end tell
                       """
        num = osa.communicate(panes_script)[0]

        return num.strip()

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

        # If we have just one pane we don't need to do any splitting.
        if num_panes <= 1:
            return

        # tmux seems to treat the first 2 tiles of a tiled layout like this
        if num_panes == 2:
            if layout == 'tiled':
                layout = 'even-vertical'

        # 'even-horizontal' layouts just split vertically across the screen
        if layout == 'even-horizontal':

            for p in range(2, num_panes+1):
                self.applescript.append(create_pane(p-1, p, "vertical"))

        # 'even-vertical' layouts just split horizontally down the screen
        elif layout == 'even-vertical':

            for p in range(2, num_panes+1):
                self.applescript.append(create_pane(p-1, p, "horizontal"))

        # 'main-vertical' layouts have one left pane that is full height,
        # and then split the remaining panes horizontally down the right
        elif layout == 'main-vertical':

            self.applescript.append(create_pane(1, 2, "vertical"))
            for p in range(3, num_panes+1):
                self.applescript.append(create_pane(p-1, p, "horizontal"))

        # 'main-vertical-flipped' layouts have one right pane that is full height,
        # and then split the remaining panes horizontally down the left
        elif layout == 'main-vertical-flipped':

            self.applescript.append(create_pane(1, num_panes, "vertical"))
            for p in range(2, num_panes):
                self.applescript.append(create_pane(p-1, p, "horizontal"))

        # 'main-horizontal' layouts have one left pane that is full height,
        # and then split the remaining panes horizontally down the right
        elif layout == 'main-horizontal':

            self.applescript.append(create_pane(1, 2, "horizontal"))
            for p in range(3, num_panes+1):
                self.applescript.append(create_pane(p-1, p, "vertical"))

        # 'double-main-horizontal' layouts have two left panes that are full height,
        # and then split the remaining panes horizontally down the right
        elif layout == 'double-main-horizontal':

            self.applescript.append(create_pane(1, num_panes-1, "horizontal"))
            self.applescript.append(create_pane(num_panes-1, num_panes, "vertical"))
            for p in range(2, num_panes-1):
                self.applescript.append(create_pane(p-1, p, "vertical"))

        # 'double-main-vertical' layouts have two bottom panes that spllit the width
        # and then split the remaining panes vertically across the top
        elif layout == 'double-main-vertical':

            self.applescript.append(create_pane(1, 2, "vertical"))
            self.applescript.append(create_pane(2, 3, "vertical"))
            for p in range(4, num_panes+1):
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

        # '3_columns' layouts create 3 columns and then however many rows as
        # needed. If there are odd number of panes then the bottom pane
        # spans two columns. Panes are numbered top to bottom, left to right.
        elif layout == '3_columns':

            vertical_splits = int(ceil((num_panes / 3.0))) - 1
            second_columns = num_panes / 3
            i = 1

            for p in range(0, vertical_splits):
                pp = (p * 3) + 1
                cp = pp + 3
                i += 1
                self.applescript.append(create_pane(pp, cp, "horizontal"))

            for p in range(0, vertical_splits+1):
                pp = (p * 3) + 1
                for q in range(0, 2):
                    if i >= num_panes:
                        break
                    qp = pp + q
                    cp = pp + 1 + q
                    i += 1
                    self.applescript.append(create_pane(qp, cp, "vertical"))

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

        # If we have just one pane we don't need to do any splitting.
        if num_panes <= 1:
            return

        # tmux seems to treat the first 2 tiles of a tiled layout like this
        if num_panes == 2 and layout == 'tiled':
            layout = 'even-vertical'

        # 'even-horizontal' layouts just split vertically across the screen
        if layout == 'even-horizontal':

            for p in range(2, num_panes+1):
                self.applescript.append(prefix + 'keystroke "d" using command down')

            # Focus back on the first pane
            self.applescript.append(prefix + 'keystroke "]" using command down')

        # 'even-vertical' layouts just split horizontally down the screen
        elif layout == 'even-vertical':

            for p in range(2, num_panes+1):
                self.applescript.append(prefix + 'keystroke "D" using command down')

            # Focus back on the first pane
            self.applescript.append(prefix + 'keystroke "]" using command down')

        # 'main-vertical' layouts have one left pane that is full height,
        # and then split the remaining panes horizontally down the right
        elif layout == 'main-vertical':

            self.applescript.append(prefix + 'keystroke "d" using command down')
            for p in range(3, num_panes+1):
                self.applescript.append(prefix + 'keystroke "D" using command down')

            # Focus back on the first pane
            self.applescript.append(prefix + 'keystroke "]" using command down')

        # 'main-vertical-flipped' layouts have one right pane that is full height,
        # and then split the remaining panes horizontally down the left
        elif layout == 'main-vertical-flipped':

            self.applescript.append(prefix + 'keystroke "d" using command down')

            # Focus back on the first pane
            self.applescript.append(prefix + 'keystroke "[" using command down')

            for p in range(3, num_panes+1):
                self.applescript.append(prefix + 'keystroke "D" using command down')

        # 'main-horizontal' layouts have one left pane  that is full height,
        # and then split the remaining panes horizontally down the right
        elif layout == 'main-horizontal':

            self.applescript.append(prefix + 'keystroke "D" using command down')
            for p in range(3, num_panes+1):
                self.applescript.append(prefix + 'keystroke "d" using command down')

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

        # '3_columns' layouts create 3 columns and then however many rows as
        # needed. If there are odd number of panes then the bottom pane
        # spans two columns. Panes are numbered top to bottom, left to right.
        elif layout == '3_columns':

            vertical_splits = int(ceil((num_panes / 3.0))) - 1

            i = 1
            for p in range(0, vertical_splits):
                self.applescript.append(prefix + 'keystroke "D" using command down')
                i += 1

            while True:
                self.applescript.append(prefix + 'keystroke "]" using command down')
                i += 1
                self.applescript.append(prefix + 'keystroke "d" using command down')
                if i >= num_panes:
                    break
                i += 1
                self.applescript.append(prefix + 'keystroke "d" using command down')
                if i >= num_panes:
                    break

        # 'double-main-horizontal' layouts have two left panes that are full height,
        # and then split the remaining panes horizontally down the right
        elif layout == 'double-main-horizontal':

            self.applescript.append(prefix + 'keystroke "d" using command down')
            if num_panes > 2:
                self.applescript.append(prefix + 'keystroke "d" using command down')

            if num_panes > 3:
                for p in range(0, num_panes-3):
                    self.applescript.append(prefix + 'keystroke "D" using command down')

        # 'double-main-vertical' layouts have two bottom panes that split the width
        # and then split the remaining panes vertically across the top
        elif layout == 'double-main-vertical':

            self.applescript.append(prefix + 'keystroke "D" using command down')
            self.applescript.append(prefix + 'keystroke "d" using command down')

            self.applescript.append(prefix + 'keystroke "]" using command down')
            if num_panes > 3:
                for p in range(0, num_panes-3):
                    self.applescript.append(prefix + 'keystroke "d" using command down')

        # Raise an exception if we don't recognise the layout setting.
        else:
            raise ValueError("Unknown layout setting.")

        # This is all keystroke based and thus takes a moment to happen,
        # so unfortunately (for old iTerm) we have to wait a moment to
        # give all that time to happen.
        self.applescript.append('delay 2')

    def initiate_pane(self, pane, commands="", name=None):
        """ Once we have layed out the panes we need, we can now navigate
            to the specified starting directory and run the specified
            commands for each pane.
        """

        # Determine the correct target for Applescript's 'tell' command
        # based upon iTerm version.
        if self.new_iterm:
            tell_target = 'pane_%s' % pane
        else:
            # Converts numbers to 2nd, 3rd, 4th format for Applescript
            ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
            tell_target = ordinal(pane) + ' session of current terminal'

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

    def initiate_window(self, commands=None):
        """ Runs the list of commands in the current pane
        """
        command = "; ".join(commands)
        self.applescript.append(
            ''' tell current session of current window
                    write text "{command}"
                end tell
            '''.format(command=command))

    def focus_on_pane(self, pane):
        """ Switch focus to the specified pane.
        """

        if not pane:
            return

        if not self.new_iterm and not self.here:
            pane -= 1

        # Determine the correct target for Applescript's 'tell' command
        # based upon iTerm version.
        if self.new_iterm:
            self.applescript.append(''' tell pane_{pane}
                                        select
                                    end tell
                                '''.format(pane=pane))
        else:
            for i in range(1, pane):
                self.applescript.append('tell i term application "System Events" ' +
                                        'to keystroke "]" using command down')

    def process_file(self):
        """ Parse the named iTermocil file, generate Applescript to send to
            iTerm2 to generate panes, name them and run the specified commands
            in them.
        """

        # total_pane_count is only used for old iTerm, and is needed to
        # reference panes created in later windows
        if self.new_iterm:
            total_pane_count = 0
        else:
            total_pane_count = int(self.get_num_panes_in_current_window())
            if self.here:
                total_pane_count -= 1

        if 'windows' not in self.parsed_config:
            print "ERROR: No windows defined in " + self.file
            sys.exit(1)

        for num, window in enumerate(self.parsed_config['windows']):
            if num > 0:
                if self.new_iterm:
                    self.applescript.append('tell current window')
                    self.applescript.append('create tab with default profile')
                    self.applescript.append('end tell')
                    # self.applescript.append('create window with default profile')
                else:
                    self.applescript.append('delay 0.3')
                    self.applescript.append('tell i term application "System Events" ' +
                                            'to keystroke "t" using command down')
                    self.applescript.append('delay 0.3')

            base_command = []

            # Extract layout format, if given.
            if "layout" in window:
                layout = window['layout']
            else:
                layout = "tiled"

            # Extract starting directory for panes in this window, if given.
            if 'root' in window:
                if window['root']:
                    parsed_path = window['root'].replace(" ", "\\\ ")
                    base_command.append('cd {path}'.format(path=parsed_path))
                else:
                    if self.here:
                        parsed_path = self.cwd.replace(" ", "\\\ ")
                        base_command.append('cd {path}'.format(path=parsed_path))
                    pass
            else:
                print 'no root!'

            # Generate Applescript to lay the panes out and then add to our
            # Applescript commands to run.
            if 'panes' in window:

                if self.new_iterm:
                    self.arrange_panes(len(window['panes']), layout)
                else:
                    self.arrange_panes_old_iterm(len(window['panes']), layout)

                focus_pane = None
                if self.new_iterm:
                    start_pane = 1
                else:
                    start_pane = total_pane_count + 1

                for pane_num, pane in enumerate(window['panes'], start=start_pane):
                    total_pane_count += 1
                    pane_name = None

                    # each pane needs the base_command to navigate to
                    # the correct directory
                    pane_commands = []
                    pane_commands.extend(base_command)

                    # pane entries may be lists of multiple commands
                    if isinstance(pane, dict):
                        if 'commands' in pane:
                            for command in pane['commands']:
                                escaped_command = command.replace('"', r'\"')
                                pane_commands.append(escaped_command)

                        if 'name' in pane:
                            pane_name = pane.get('name', None)

                        if 'focus' in pane:
                            focus_pane = pane_num

                    else:
                        escaped_command = pane.replace('"', r'\"')
                        pane_commands.append(escaped_command)

                    # Check if this pane, or containing window has a name.
                    if pane_name:
                        window_name = pane_name
                    else:
                        window_name = window.get('name', None)

                    self.initiate_pane(pane_num, pane_commands, window_name)

                self.focus_on_pane(focus_pane)

            else:
                commands = []
                if 'command' in window:
                    commands = window['command']
                elif 'commands' in window:
                    commands = window['commands']
                self.initiate_window(commands)


def main():

    parser = argparse.ArgumentParser(
        description='Process a teamocil file natively in iTerm2 (i.e. without tmux).',
        usage='%(prog)s [options] <layout>'
    )

    parser.add_argument("layout_name",
                        help="the layout name you wish to process",
                        metavar="layout",
                        nargs="*")

    # teamocil compatible flags:

    parser.add_argument("--here",
                        help="run in the current terminal",
                        action="store_true",
                        default=False)

    parser.add_argument("--edit",
                        help="edit file in $EDITOR if set, otherwise open in GUI",
                        action="store_true",
                        default=False)

    parser.add_argument("--show",
                        help="show the layout instead of executing it",
                        action="store_true",
                        default=False)

    parser.add_argument("--layout",
                        help="specify a layout file rather looking in the ~/.teamocil",
                        action="store_true",
                        default=None)

    parser.add_argument("--list",
                        help="show the available layouts in ~/teamocil",
                        action="store_true",
                        default=False)

    parser.add_argument("--version",
                        help="show iTermocil version",
                        action="store_true",
                        default=None)

    parser.add_argument("--debug",
                        help="output the iTerm Applescript instead of executing it",
                        action="store_true",
                        default=None)

    args = parser.parse_args()

    # itermocil files live in a hidden directory in the home directory
    # either in an .itermocil directory or a .teamocil directory
    itermocil_dir = os.path.join(os.path.expanduser("~"), ".itermocil")
    teamocil_dir = os.path.join(os.path.expanduser("~"), ".teamocil")

    # If --version then show the version number
    if args.version:
        print __version__
        sys.exit(0)

    # If --list then show the layout names in ~./teamocil
    if args.list:
        for d in [itermocil_dir, teamocil_dir]:
            if os.path.isdir(d):
                print d
                for file in os.listdir(d):
                    if file.endswith(".yml"):
                        print("  " + file[:-4])
        sys.exit(0)

    filepath = None
    if not args.layout_name:
        # parser.error('You must supply a layout name, or just the --list option. Use -h for help.')
        filepath = os.path.join(os.getcwd(), 'iTermocil.yml')
        if not os.path.isfile(filepath):
            parser.print_help()
            sys.exit(1)
    else:
        layout = args.layout_name[0]
        # Sanitize input
        layout = re.sub("[\*\?\[\]\'\"\\\$\;\&\(\)\|\^\<\>]", "", layout)

    # Build teamocil file path based on presence of --layout flag.
    if args.layout:
        filepath = os.path.join(os.getcwd(), layout)
    else:
        if not os.path.isdir(itermocil_dir):
            if not os.path.isdir(teamocil_dir):
                print "ERROR: No ~/.itermocil or ~/.teamocil directory"
                sys.exit(1)

        if not filepath:
            filepath = os.path.join(itermocil_dir, layout + ".yml")
            if not os.path.isfile(filepath):
                filepath = os.path.join(teamocil_dir, layout + ".yml")

    # If --edit the try to launch editor and exit
    if args.edit:
        editor_var = os.getenv('EDITOR')
        if editor_var:
            import shlex
            editor = shlex.split(editor_var)
            editor.append(filepath)
            subprocess.call(editor)
        else:
            if not os.path.isfile(filepath):
                subprocess.call(['touch', filepath])
            subprocess.call(['open', filepath])

        sys.exit(0)

    # Check teamocil file exists
    if not os.path.isfile(filepath):
        print "ERROR: There is no file at: " + filepath
        sys.exit(1)

    # If --show then output and exit()
    if args.show:
        with open(filepath, 'r') as fin:
            print fin.read()
            sys.exit(0)

    # Parse the teamocil file and execute it.
    cwd = os.getcwd()
    instance = Itermocil(filepath, here=args.here, cwd=cwd)

    # If --debug then output the applescript. Do some rough'n'ready
    # formatting on it.
    if args.debug:

        script = instance.script()
        script = re.sub("^(\s*)", "", script, flags=re.MULTILINE)

        indent = ""
        formatted_script = []

        for line in script.split("\n"):
            if line[:8] == "end tell":
                indent = indent[:-1]
            if line[:4] == "tell" and line[:7] != "tell i ":
                formatted_script.append("")

            formatted_script.append(indent + line)

            if line[:4] == "tell" and line[:7] != "tell i ":
                indent += "\t"

        formatted_script.append("")
        print "\n".join(formatted_script)
    else:
        instance.execute()


if __name__ == '__main__':
    main()
