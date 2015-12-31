## Intro

iTermocil allows you to setup pre-configured layouts of windows and panes in [iTerm2](https://iterm2.com/); see the [README](https://github.com/TomAnthony/itermocil/blob/master/README.md)

This page includes information about additional layouts.

## Layouts

There are a variety of [example layout files](https://github.com/TomAnthony/itermocil/tree/master/test_layouts) in this repo.

### even-horizontal

Create as many even spaced columns as needed, in a single row. This is the same as tmux's even-horizontal layout.

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
| (0) git status   | (1) rails server |
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

### even-vertical

Create as many even spaced rows as needed, in a single column. This is the same as tmux's even-vertical layout.

```yaml
windows:
  - name: sample-two-panes
    root: ~/Code/sample/www
    layout: even-vertical
    panes:
      - git status
      - rails server
```

```
.-------------------------------------.
| (0) git status                      |
|                                     |
|                                     |
|                                     |
|-------------------------------------|
| (1) rails server                    |
|                                     |
|                                     |
|                                     |
'-------------------------------------'
```

### main-vertical

Create a left pane spanning the full height of the window, and then in a right column as many evenly spaced rows as needed. This is the same as tmux's main-vertical layout.

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

```
.------------------.------------------.
| (0) vim          | (1) git pull     |
|                  |     git status   |
|                  |                  |
|                  |                  |
|                  |------------------|
|                  | (2) rails server |
|                  |                  |
|                  |                  |
|                  |                  |
'------------------'------------------'
```

### main-vertical-flipped

Create a right pane spanning the full height of the window, and then in a left column as many evenly spaced rows as needed.

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
| (0) git pull     | (2) vim          |
|     git status   |                  |
|                  |                  |
|                  |                  |
|------------------|                  |
| (1) rails server |                  |
|                  |                  |
|                  |                  |
|                  |                  |
'------------------'------------------'
```

### tiled

Create 2 columns and as many rows as needed. An uneven number of panes will mean the bottom row spans both columns. This is the same as tmux's tiled layout.

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
.----------------------.----------------------.
| (0) vim              | (1)foreman start web |
|                      |                      |
|                      |                      |
|                      |                      |
|----------------------|----------------------|
| (2) git status       | (3) foreman start w..|
|                      |                      |
|                      |                      |
|                      |                      |
'----------------------'----------------------'
```

### 3_columns

Creates 3 columns and then however many rows as needed. If the number of panes isn't divisible by 3 then the final row will have fewer columns.

```yaml
windows:
  - name: sample-3-columns
    root: ~
    layout: 3_columns
    panes:
      - echo "pane 1"
      - echo "pane 2"
      - echo "pane 3"
      - echo "pane 4"
      - echo "pane 5"
      - echo "pane 6"
      - echo "pane 7"
      - echo "pane 8"
      - echo "pane 9"
```

```
.------------.------------.------------.
| (0)        | (1)        | (2)        |
|            |            |            |
|            |            |            |
|------------|------------|------------|
| (3)        | (4)        | (5)        |
|            |            |            |
|            |            |            |
|------------|------------|------------|
| (6)        | (7)        | (8)        |
|            |            |            |
|            |            |            |
'------------'------------'------------'
```

### double-main-horizontal

Create 2 rows. The bottom row is 2 full width columns and the top row is split into as many columns as needed.

```yaml
windows:
  - name: sample-five-panes
    root: ~/Code/sample/www
    layout: double-main-horizontal
    panes:
      - vim
      - git log
      - guard
      - rails console
      - tail -f log/development.log
```

```
.-----------.-------------.-----------.
| (0)       | (1)         | (2)       |
|           |             |           |
|           |             |           |
|           |             |           |
|-----------'------.------'-----------|
| (4)              | (3)              |
|                  |                  |
|                  |                  |
|                  |                  |
|                  |                  |
'------------------'------------------'
```

### double-main-vertical

Create 2 full height columns on the left, and a third column with as many rows as needed.

```yaml
windows:
  - name: sample-double-main
    root: ~/Code/sample/www
    layout: double-main-vertical
    panes:
      - vim
      - git log
      - guard
      - tail -f log/development.log
      - rails console
```

```
.-----------.-------------.-----------.
| (0)       | (1)         | (2)       |
|           |             |           |
|           |             |-----------|
|           |             | (3)       |
|           |             |           |
|           |             |-----------|
|           |             | (4)       |
|           |             |           |
|           |             |           |
'-----------'-------------'-----------'
```