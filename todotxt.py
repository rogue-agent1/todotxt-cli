#!/usr/bin/env python3
"""todotxt - todo.txt CLI manager (todotxt format). Zero deps."""
import sys, os, re, json
from datetime import datetime

TODO_FILE = os.environ.get("TODO_FILE", "todo.txt")
DONE_FILE = os.environ.get("DONE_FILE", "done.txt")

def load(path):
    if not os.path.exists(path): return []
    with open(path) as f:
        return [l.rstrip("\n") for l in f if l.strip()]

def save(path, items):
    with open(path, "w") as f:
        for item in items: f.write(item + "\n")

def parse_task(line):
    t = {"raw": line, "done": False, "priority": "", "date": "", "text": "", "projects": [], "contexts": []}
    s = line
    if s.startswith("x "):
        t["done"] = True; s = s[2:].strip()
    m = re.match(r'^\(([A-Z])\)\s+', s)
    if m: t["priority"] = m.group(1); s = s[m.end():]
    m = re.match(r'^(\d{4}-\d{2}-\d{2})\s+', s)
    if m: t["date"] = m.group(1); s = s[m.end():]
    t["text"] = s
    t["projects"] = re.findall(r'\+(\S+)', s)
    t["contexts"] = re.findall(r'@(\S+)', s)
    return t

def format_task(idx, line):
    t = parse_task(line)
    status = "✅" if t["done"] else "⬜"
    pri = f"({t['priority']}) " if t["priority"] else ""
    return f"  {idx:3d}. {status} {pri}{t['text']}"

def cmd_add(args):
    if not args: print("Usage: todotxt add <task>"); sys.exit(1)
    task = " ".join(args)
    date = datetime.now().strftime("%Y-%m-%d")
    line = f"{date} {task}"
    items = load(TODO_FILE)
    items.append(line)
    save(TODO_FILE, items)
    print(f"✅ Added #{len(items)}: {task}")

def cmd_list(args):
    items = load(TODO_FILE)
    if not items: print("No tasks."); return
    # Filters
    project = context = priority = None
    for i, a in enumerate(args):
        if a.startswith("+"): project = a[1:]
        elif a.startswith("@"): context = a[1:]
        elif a.startswith("-p"): priority = args[i+1].upper() if i+1 < len(args) else None
    
    for idx, line in enumerate(items, 1):
        t = parse_task(line)
        if project and project not in t["projects"]: continue
        if context and context not in t["contexts"]: continue
        if priority and t["priority"] != priority: continue
        print(format_task(idx, line))
    print(f"\n  {len(items)} task(s) total")

def cmd_done(args):
    if not args: print("Usage: todotxt done <number>"); sys.exit(1)
    num = int(args[0])
    items = load(TODO_FILE)
    if num < 1 or num > len(items): print(f"❌ Invalid #{num}"); sys.exit(1)
    line = items[num-1]
    if not line.startswith("x "):
        done_line = f"x {datetime.now().strftime('%Y-%m-%d')} {line}"
        items[num-1] = done_line
        save(TODO_FILE, items)
        # Also append to done.txt
        with open(DONE_FILE, "a") as f: f.write(done_line + "\n")
        print(f"✅ Completed #{num}")
    else:
        print(f"Already done: #{num}")

def cmd_pri(args):
    if len(args) < 2: print("Usage: todotxt pri <number> <A-Z>"); sys.exit(1)
    num, pri = int(args[0]), args[1].upper()
    items = load(TODO_FILE)
    if num < 1 or num > len(items): print(f"❌ Invalid #{num}"); sys.exit(1)
    line = items[num-1]
    # Remove existing priority
    line = re.sub(r'^\([A-Z]\)\s+', '', line)
    items[num-1] = f"({pri}) {line}"
    save(TODO_FILE, items)
    print(f"✅ Set #{num} priority to ({pri})")

def cmd_rm(args):
    if not args: print("Usage: todotxt rm <number>"); sys.exit(1)
    num = int(args[0])
    items = load(TODO_FILE)
    if num < 1 or num > len(items): print(f"❌ Invalid #{num}"); sys.exit(1)
    removed = items.pop(num-1)
    save(TODO_FILE, items)
    print(f"🗑️ Removed #{num}: {parse_task(removed)['text']}")

def cmd_search(args):
    if not args: print("Usage: todotxt search <query>"); sys.exit(1)
    q = " ".join(args).lower()
    items = load(TODO_FILE)
    for idx, line in enumerate(items, 1):
        if q in line.lower():
            print(format_task(idx, line))

def cmd_stats(args):
    items = load(TODO_FILE)
    done = load(DONE_FILE)
    tasks = [parse_task(l) for l in items]
    open_t = [t for t in tasks if not t["done"]]
    done_t = [t for t in tasks if t["done"]]
    projects = set()
    contexts = set()
    for t in tasks:
        projects.update(t["projects"])
        contexts.update(t["contexts"])
    print(f"📊 Stats")
    print(f"  Open: {len(open_t)}  Done: {len(done_t) + len(done)}  Total: {len(items) + len(done)}")
    if projects: print(f"  Projects: {', '.join(sorted(projects))}")
    if contexts: print(f"  Contexts: {', '.join(sorted(contexts))}")

CMDS = {"add":cmd_add,"list":cmd_list,"ls":cmd_list,"done":cmd_done,"do":cmd_done,
        "pri":cmd_pri,"rm":cmd_rm,"del":cmd_rm,"search":cmd_search,"s":cmd_search,"stats":cmd_stats}

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h","--help"):
        print("todotxt - todo.txt task manager")
        print("Commands: add, list, done, pri, rm, search, stats")
        print("Filters: +project, @context, -p PRIORITY")
        sys.exit(0)
    cmd = args[0]
    if cmd not in CMDS: print(f"Unknown: {cmd}"); sys.exit(1)
    CMDS[cmd](args[1:])
