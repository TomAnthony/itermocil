## Introduction

iTermocil allows you to setup pre-configured layouts of windows and panes in [iTerm2](https://iterm2.com/), having each open in a specified directory and execute specified commands. You do this by writing YAML files to save your layouts. If your using session restoration or saved window layouts in iTerm, you should find iTermocil is a nice upgrade on that.

iTermocil supports iTerm 2.x and the new 3.x (including later betas). It works better with the new 3.x versions which have improved Applescript support.

![Example](https://raw.githubusercontent.com/TomAnthony/itermocil/master/itermocil.gif)

## Installing iTermocil

```bash
# Install `itermocil` via Homebrew
$ brew update
$ brew install TomAnthony/brews/itermocil

# Create your layout directory
$ mkdir ~/.itermocil

# Edit ~/.itermocil/sample.yml (look for sample layouts in this very `README.md`)
# There are also a variety of example files in 'test_layouts' directory in this repo
$ itermocil --edit sample

# Run your newly-created sample layout
$ itermocil sample

# Note that you can also used ~/.teamocil as your directory, if you're a teamocil user.
```

## Using iTermocil

```bash
$ itermocil [options] <layout-name>
```

Alternatively, if you have an `iTermocil.yml` file in the current directory you can simply run `itermocil` and it will use that file, so you can have files inside your projects and sync via Github etc:

```bash
$ cd my_project
$ itermocil
```

iTermocil is compatible with all of teamocil's flags, and they all work in the same way.

### Global options

| Option      | Description
|-------------|----------------------------
| `--list`    | Lists all available layouts in `~/.itermocil`

### Layout options

| Option      | Description
|-------------|----------------------------
| `--layout`  | Takes a custom file path to a YAML layout file instead of `[layout-name]`
| `--here`    | Uses the current window as the layout’s first window
| `--edit`    | Edit the layout file in either `$EDITOR` or your preferred GUI editor
| `--show`    | Shows the layout content instead of executing it

## Configuration

### Session

| Key       | Description
|-----------|----------------------------
| `name`    | This is currently ignored in iTermocil as there is no tmux session.
| `windows` | An `Array` of windows
| `pre`     | Command that get executes before all other actions.

### Windows

| Key        | Description
|------------|----------------------------
| `name`     | All iTerm panes in this window will be given this name.
| `root`     | The path where all panes in the window will be started
| `layout`   | The layout format that iTermocil will use (see below)
| `panes`    | An `Array` of panes
| `command`  | A command to run in the current window. Ignored if `panes` is present
| `commands` | An array of commands for run in the current window. Ignored if either `panes` or `command `is present
| `focus`    | This is currently unsupported in iTermocil


### Panes

A pane can either be a `String` or a `Hash`. If it’s a `String`, Teamocil will treat it as a single-command pane.

| Key        | Description
|------------|----------------------------
| `commands` | An `Array` of commands that will be ran when the pane is created
| `focus`    | If set to `true`, the pane will be selected after the layout has been executed

## Examples

See some example of various layouts below, or see [Layouts](https://github.com/TomAnthony/itermocil/blob/master/LAYOUTS.md) for more information on the available layouts. There is also a variety of [example layout files](https://github.com/TomAnthony/itermocil/tree/master/test_layouts) in this repo.

### Simple two pane window

```yaml
windows:
  - name: sample-two-panes
    root: ~/Code/sample/www
    layout: even-horizontal
    panes:
      - git status
      - rails server
```

```
.------------------.------------------.
| (0)              | (1)              |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |                  |
'------------------'------------------'
```

### Simple three pane window

```yaml
windows:
  - name: sample-three-panes
    root: ~/Code/sample/www
    layout: main-vertical
    panes:
      - vim
      - commands:
        - git pull
        - git status
        name: 'git'
      - rails server
```
Note: the 'name' directive in 'commands' in an iTermocil specific addition, which will cause teamocil to fail if it tries to parse the file.

```
.------------------.------------------.
| (0)              | (1)              |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |------------------|
|                  | (2)              |
|                  |                  |
|                  |                  |
|                  |                  |
'------------------'------------------'
```

### Simple three pane window (flipped)

```yaml
windows:
  - name: sample-three-panes
    root: ~/Code/sample/www
    layout: main-vertical-flipped
    panes:
      - commands:
        - git pull
        - git status
      - rails server
      - vim
```

```
.------------------.------------------.
| (0)              | (2)              |
|                  |                  |
|                  |                  |
|                  |                  |
|------------------|                  |
| (1)              |                  |
|                  |                  |
|                  |                  |
|                  |                  |
'------------------'------------------'
```

### Simple four pane window

```yaml
windows:
  - name: sample-four-panes
    root: ~/Code/sample/www
    layout: tiled
    panes:
      - vim
      - foreman start web
      - git status
      - foreman start worker
```

```
.------------------.------------------.
| (0)              | (1)              |
|                  |                  |
|                  |                  |
|                  |                  |
|------------------|------------------|
| (2)              | (3)              |
|                  |                  |
|                  |                  |
|                  |                  |
'------------------'------------------'
```

### Two pane window with focus in second pane

```yaml
windows:
  - name: sample-two-panes
    root: ~/Code/sample/www
    layout: even-horizontal
    panes:
      - rails server
      - commands:
          - rails console
        focus: true
```

```
.------------------.------------------.
| (0)              | (1) <focus here> |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |                  |
'------------------'------------------'
```

### A pane-less window

```yaml
windows:
  - name: pane-less
    root: ~/Code/sample/www
    command: rails console
windows:
  - name: one_more-pane-less
    root: ~/Code/sample/www
    commands:
      - bundle update
      - rails server
```

### Additional Layouts

In the [Layouts](https://github.com/TomAnthony/itermocil/blob/master/LAYOUTS.md) file you can see these additional layouts:

- 3_columns - 3 columns with as many rows as needed
- double-main-vertical - 2 left full height columns, and a third multi-row column
- double-main-horizontal - 2 rows, where bottom row is 2 full width columns, and top row is multi-column

## teamocil

iTermocil was originally inspired by and is compatible with [teamocil](https://github.com/remiprev/teamocil), allowing anyone with teamocil files to execute those files natively in iTerm2, without needing tmux or any other dependency. However, iTermocil also has support for additional directives which will cause teamocil to fail, if used.

## Notes

Teamocil allows supplying a name for a tmux session which has no purpose in iTerm, and so that option is ignored.

In tmux it is 'windows' that have names, whereas in iTerm each pane in a window can have a name. iTermocil will name all the child panes of a window by the window name given in a termocil file.

iTermocil works for iTerm 2+, but the script support is better in iTerm 2.9 beta so things run a bit faster/cleaner with iTerm 2.9+. If using beta builds you should grab the [latest nightly](https://iterm2.com/nightly/latest), as the 2.9.20150626 'recommended beta' build does not have the required script hooks for iTermocil to work (and I have no plans to kludge something just for an incomplete beta that will never be released).

Currently, everything is Python 2 and so if you are using Python 3 by default you may need to tweak the #! line.

## Shell autocompletion

### Zsh autocompletion

To get autocompletion when typing `itermocil <Tab>` in a zsh session, add this line to your `~/.zshrc` file:

```zsh
compctl -g '~/.itermocil/*(:t:r)' itermocil
```

### Bash autocompletion

To get autocompletion when typing `itermocil <Tab>` in a bash session, add this line to your `~/.bashrc` file:

```bash
complete -W "$(itermocil --list)" itermocil
```

### fish autocompletion

To get autocompletion when typing `itermocil <Tab>` in a fish session, add this line to your `~/.config/fish/config.fish` file:

```fish
complete -c itermocil -a "(itermocil --list)"
```

## Contributors

I'd love any ideas/feedback/thoughts, please open [an issue](https://github.com/TomAnthony/itermocil/issues) or create a [fork](https://github.com/TomAnthony/itermocil/fork) and send a pull request, like these wonderful people:

- [onthestairs](https://github.com/onthestairs)
- [jefftriplett](https://github.com/jefftriplett)
- [febLey](https://github.com/febLey)
- [rebeling](https://github.com/rebeling)
- [adityavarma1234](https://github.com/adityavarma1234)
- [chris838](https://github.com/chris838)
- [mattmartini](https://github.com/mattmartini)
- [glasnoster](https://github.com/glasnoster)
- [bitsapien](https://github.com/bitsapien)
- [galaxyutii](https://github.com/galaxyutii)
- [mbollemeijer](https://github.com/mbollemeijer)
- [mcky](https://github.com/mcky)

A huge thanks to [Rémi Prévost](http://www.exomel.com/en) who authored [teamocil](https://github.com/remiprev/teamocil), which inspired iTermocil. It is a fantastic tool, and I'm hoping that iTermocil helps more people discover teamocil.

## To Do

- make a way to 'save' the current layout (not sure is possible)
- add tmuxinator file support
- add support for bespoke file format to support things like iTerm badges and tab colours
- possibly add a flag for using windows instead of tabs for new 'windows'
- pane 'focus' is supported, but window 'focus' is not yet - I'm not sure how to focus on a certain window still
- with the --edit flag, if no $EDITOR is set and a new layout name is given, then an empty file is created to be opened in a GUI editor. Is there a better way to handle this? Maybe clean up blank files whenever itermocil is launched?

## License

iTermocil is © 2016 [Tom Anthony](https://twitter.com/tomanthonyseo) and may be freely distributed under the [MIT license](https://github.com/TomAnthony/itermocil/blob/master/LICENSE.md). See the LICENSE file for more information.
