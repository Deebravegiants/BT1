# [H] gix's submodule name validation bypass + trust inheritance flaw enables path traversal and credential disclosure

## Summary
Severity: High
Advisory: GHSA-p3hw-mv63-rf9w
CWE: CWE-200, CWE-22
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-p3hw-mv63-rf9w
Type: github-advisory

## Affected
- crates.io: `gix` — affected >=0 <0.83.0
- crates.io: `gix-validate` — affected >=0 <0.11.1

## Details
### Summary

Submodule name validation bypass plus missing validation in production code paths allows path traversal via crafted `.gitmodules`. Combined with a trust inheritance flaw in `Submodule::open()`, this enables reading arbitrary git repository configs (including credentials) from traversed paths with full trust (CWE-22, CWE-200).

### Details

**Bug 1: Validation bypass in `gix-validate/src/submodule.rs` (lines 27-42)**

The `name()` function uses `name.find(b"..")` which returns only the FIRST occurrence. If the first `..` is embedded in a non-traversal context, the function returns `Ok` without checking subsequent `../` sequences:

```rust
pub fn name(name: &BStr) -> Result<&BStr, name::Error> {
    match name.find(b"..") {
        Some(pos) => {
            let &b = name.get(pos + 2).ok_or(name::Error::ParentComponent)?;
            if b == b'/' || b == b'\\' {
                Err(name::Error::ParentComponent)
            } else {
                Ok(name)  // Returns Ok without checking rest of string
            }
        }
        None => Ok(name),
    }
}
```

Bypass: `a..b/../../../.git/` passes because `find(b"..")` returns position 1 (the `..` in `a..b`), checks `name[3] == b'b'`, and returns Ok. The real `/../../../` is never checked.

**Bug 2: Validation never called in production**

`gix_validate::submodule::name()` has zero production callers (only test code). The `names()` iterator in `gix-submodule/src/access.rs:29` explicitly documents it returns "unvalidated names."

`git_dir()` at `gix/src/submodule/mod.rs:198-204` constructs filesystem paths from raw names:

```rust
pub fn git_dir(&self) -> PathBuf {
    self.state.repo.common_dir().join("modules").join(gix_path::from_bstr(self.name()))
}
```

**Bug 3: Trust inheritance bypass in `Submodule::open()`**

At `gix/src/submodule/mod.rs:270`, `open()` clones the parent repository's options:

```rust
match crate::open_opts(self.git_dir_try_old_form()?, self.state.repo.options.clone()) {
```

The parent's `options.git_dir_trust` is `Some(Trust::Full)`. At `gix/src/open/repository.rs:103-104`:

```rust
if options.git_dir_trust.is_none() {
    options.git_dir_trust = gix_sec::Trust::from_path_ownership(&git_dir)?.into();
}
```

Since trust is already `Some(Full)`, the ownership check is **skipped entirely**. The traversed path is opened with `Trust::Full` regardless of ownership, bypassing gitoxide's safe-directory protections.

### PoC

Compiled and executed in Rust 1.94.1 `--release` mode. All bypass cases confirmed:

```
BYPASS a..b/../../../.git/           -> PASSED validation
       git_dir = .git/modules/a..b/../../../.git/
       normalized = .git/              (parent repo!)

BYPASS x..y/../../../.git/config     -> PASSED validation
       git_dir = .git/modules/x..y/../../../.git/config
       normalized = .git/config
```

### Attack chain

1. Attacker crafts a repository with `.gitmodules`:
   ```ini
   [submodule "x..y/../../.."]
       path = innocent
       url = https://attacker.com/repo.git
   ```

2. Victim clones the repository using a tool built on gitoxide.

3. When the tool iterates submodules and calls `submodule.open()` or `submodule.status()`:
   - `git_dir()` returns `.git/modules/x..y/../../..` which resolves to the parent `.git/`
   - `open_opts()` is called with `Trust::Full` (inherited from parent, ownership check skipped)
   - The parent's `.git/config` is fully parsed

4. The returned `Repository` object exposes all config values from the traversed path:
   - `remote.origin.url` (may contain `https://user:token@github.com/...`)
   - `http.extraHeader` (often `Authorization: Bearer <token>`)
   - `credential.*` sections
   - `core.sshCommand`

5. Accessible via standard API: `repo.config_snapshot().string("http.extraHeader")`, `repo.find_remote("origin")`, etc.

### Impact

A crafted `.gitmodules` in a malicious repository causes gitoxide to open arbitrary git directories as submodule repositories with full trust, exposing their configuration including credentials. This is the same class of vulnerability as GHSA-7w47-3wg8-547c (path traversal), but through the submodule name vector with an additional trust bypass.

The trust inheritance is the critical amplifier: without it, the traversed path would undergo ownership checks that could block the attack. With it, any git directory reachable via `../` is opened with full trust.

### Honest limitations

- The traversed path must be a valid git directory (HEAD, objects/, refs/ must exist)
- The victim's tool must call `open()` or `status()` on submodules (tools that only list submodules are not affected)
- Credential exposure requires the target config to contain embedded credentials
- Submodule operations currently require explicit user action

### Suggested fix

1. Fix the validation to check ALL `..` occurrences (iterate, not single `find`)
2. Call `gix_validate::submodule::name()` in `git_dir()` before constructing the path
3. Do NOT inherit `git_dir_trust` from parent when opening submodule repos -- always re-derive trust from path ownership

### Severity

High. Network vector (via clone), requires user interaction (submodule operations). The trust bypass enables credential disclosure from traversed git directories. Confidentiality impact is high.

## References
- https://github.com/GitoxideLabs/gitoxide/security/advisories/GHSA-p3hw-mv63-rf9w
- https://github.com/GitoxideLabs/gitoxide
