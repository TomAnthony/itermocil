## Introduction

iTermocil allows you setup pre-configured layouts of windows and panes in [iTerm2](https://iterm2.com/), having each open in a specified directory and execute specified commands. You do this by writing YAML files.

iTermocil is inspired by and compatible with [teamocil](https://github.com/remiprev/teamocil), allowing anyone with teamocil files to execute those files natively in iTerm2, without needing tmux or any other dependency.

If you are using the iTerm 2.9 beta then see then notes section below.

![Example](https://raw.githubusercontent.com/TomAnthony/itermocil/master/itermocil.gif)

## Installing iTermocil

```bash
# Install `itermocil` via Homebrew
$ brew install TomAnthony/brews/itermocil

# Create your layout directory
$ mkdir ~/.teamocil

# Edit ~/.teamocil/sample.yml (look for sample layouts in this very `README.md`)
$ itermocil --edit sample

# Run your newly-created sample layout
$ itermocil sample
```

## Using iTermocil

```bash
$ itermocil [options] <layout-name>
```

iTermocil is compatible with all of teamocil's flags, and they all work in the same way.

### Global options

| Option      | Description
|-------------|----------------------------
| `--list`    | Lists all available layouts in `~/.teamocil`

### Layout options

| Option      | Description
|-------------|----------------------------
| `--layout`  | Takes a custom file path to a YAML layout file instead of `[layout-name]`
| `--here`    | Uses the current window as the layout’s first window
| `--edit`    | Opens the layout file with `$EDITOR` instead of executing it
| `--show`    | Shows the layout content instead of executing it

## Configuration

### Session

| Key       | Description
|-----------|----------------------------
| `name`    | This is currently ignored in iTermocil as there is no tmux session.
| `windows` | An `Array` of windows

### Windows

| Key      | Description
|----------|----------------------------
| `name`   | All iTerm panes in this window will be given this name.
| `root`   | The path where all panes in the window will be started
| `layout` | The layout format that iTermocil will use (see below)
| `panes`  | An `Array` of panes
| `focus`  | This is currently unsupported in iTermocil

### Panes

A pane can either be a `String` or a `Hash`. If it’s a `String`, Teamocil will
treat it as a single-command pane.

| Key        | Description
|------------|----------------------------
| `commands` | An `Array` of commands that will be ran when the pane is created
| `focus`    | If set to `true`, the pane will be selected after the layout has been executed

## Examples

These examples are all borrowed from teamocil's documentation, to highlight the compatibility.

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
      - rails server
```

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

## Why I built iTermocil

I found that I primarily used tmux for the ability to have teamocil files for my projects, and to be able to zoom in to certain panes. I was never using tmux over SSH and I rarely detached from sessions locally. So everything I was doing I could do natively in iTerm2 other than opening the pre-configured sessions.

My team all use teamocil, and I had a bunch of teamocil files already, so I wrote iTermocil to enable me to keep using these files within iTerm itself.

## Notes

Teamocil allows supplying a name for a tmux session which has no purpose in iTerm, and so that option is ignored.

In tmux it is 'windows' that have names, whereas in iTerm each pane in a window can have a name. iTermocil will name all the child panes of a window by the window name given in a termocil file.

iTermocil works for iTerm 2+, but the script support is better in iTerm 2.9 beta so things run a bit faster/cleaner with iTerm 2.9+. If using beta builds should grab the [latest nightly](https://iterm2.com/nightly/latest), the 2.9.20150626 build does not have the required script hooks for iTermocil to work (and I have no plans to kludge something just for an incomplete beta).

~The only limitation on pre 2.9 iTerm is currently you cannot have the initial teamocil 'window' open in a tab, you can open with '--here' or the first 'window' will open in a new iTerm window. Subsequent 'windows' will open in tabs in that new window. I cannot find a scripting solution to work around this limitation currently.~ This now works. :)

## Thanks

A huge thanks to [Rémi Prévost](http://www.exomel.com/en) who authored [teamocil](https://github.com/remiprev/teamocil), from which I have based iTermocil. It is a fantastic tool, and I'm hoping that iTermocil helps more people discover teamocil.

## To Do

- possibly add a flag for using windows instead of tabs for new teamocil 'windows'
- ~~iTerm < 2.9 currently only works when opening new 'windows' (--here works though), iTerm betas open in tabs by default~~ Fixed.
- pane 'focus' is supported, but window 'focus' is not yet
- add 'main-horizontal' support - it is the only layout that requires pane resizing (iTerm resizes other panes to equally space them - tmux's main-horizontal progressively halves the space so each pane is smaller)
- with the --edit flag, if no $EDITOR is set and a new layout name is given, then an empty file is created to be opened in a GUI editor. Is there a better way to handle this?

## License

iTermocil is © 2015 Tom Anthony and may be freely distributed under the MIT license. See the LICENSE file for more information.