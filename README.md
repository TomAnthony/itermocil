## Introduction

iTermocil allows you open pre-configured layouts of windows and panes in [iTerm2](https://iterm2.com/), having each open in a specified directory and execute specified commands. You do this by writing YAML files.

iTermocil is inspired by and compatible with [teamocil](https://github.com/remiprev/teamocil), allowing anyone with teamocil files to execute those files natively in iTerm2, without needing tmux.

## Installing iTermocil

```bash
# Install the `iTermocil` via Homebrew
$ brew install itermocil

# OR

# Install the `iTermocil` via pip
$ pip install itermocil

# Create your layout directory
$ mkdir ~/.teamocil

# Edit ~/.teamocil/sample.yml (look for sample layouts in this very `README.md`)
$ teamocil --edit sample

# Run your newly-created sample layout
$ itermocil sample
```

## Using iTermocil

```bash
$ itermocil [options] [layout-name]
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
| `name`    | The tmux session name
| `windows` | An `Array` of windows

### Windows

| Key      | Description
|----------|----------------------------
| `name`   | The tmux window name
| `root`   | The path where all panes in the window will be started
| `layout` | The layout that will be set after all panes are created by Teamocil
| `panes`  | An `Array` of panes
| `focus`  | If set to `true`, the window will be selected after the layout has been executed

### Panes

A pane can either be a `String` or a `Hash`. If it’s a `String`, Teamocil will
treat it as a single-command pane.

| Key        | Description
|------------|----------------------------
| `commands` | An `Array` of commands that will be ran when the pane is created
| `focus`    | If set to `true`, the pane will be selected after the layout has been executed

## Examples

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

My team all use teamocil, and I had a bunch of teamocil files already, so I wrote iTermocil to enable be to keep using these files within iTerm itself.

## Thanks

A huge thanks to [Rémi Prévost](http://www.exomel.com/en) who authored [teamocil](https://github.com/remiprev/teamocil), from which I have based iTermocil. It is a fantastic tool, and I'm hoping that iTermocil helps more people discover teamocil.

## To Do

- teamocil's focus' is not yet supported ('select' works on 2.9 to do this with)
- add a command line flag for tabs vs windows for new teamocil 'windows'
- test with current iTerm (I'm on 2.9 beta version)
- teamocil's --list option
- if $EDITOR is empty, try the 'open' command (we know we are Mac based)
- make it so .itermocil also works if desired

## License

iTermocil is © 2015 Tom Anthony and may be freely distributed under the MIT license. See the LICENSE file for more information.