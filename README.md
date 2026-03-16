# todotxt

todo.txt format task manager. Zero dependencies.

## Commands

```bash
todotxt add "Task description +project @context"
todotxt list [+project] [@context] [-p A]
todotxt done <number>
todotxt pri <number> <A-Z>
todotxt rm <number>
todotxt search <query>
todotxt stats
```

## Features

- Full todo.txt format support (priorities, dates, projects, contexts)
- Completed tasks archived to done.txt
- Filter by project (+), context (@), or priority
- Stats with project/context summary

## Environment

- `TODO_FILE` — path to todo file (default: `todo.txt`)
- `DONE_FILE` — path to done file (default: `done.txt`)

## Requirements

- Python 3.6+ (stdlib only)
