# [M] OpenClaw: shell-env trusted-prefix fallback allowed attacker-controlled binary execution via $SHELL

## Summary
Severity: Medium
Advisory: GHSA-p4wh-cr8m-gm6c
CVE: CVE-2026-22217
CWE: CWE-184, CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-p4wh-cr8m-gm6c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.2.22 <2026.2.23

## Details
### Summary
`shell-env` fallback trusted prefix-based executable paths for `$SHELL`, allowing execution of attacker-controlled binaries in local/runtime-env influence scenarios.

### Details
In affected versions, shell selection accepted either:
1. a shell listed in `/etc/shells`, or
2. any executable under hardcoded trusted prefixes (`/bin`, `/usr/bin`, `/usr/local/bin`, `/opt/homebrew/bin`, `/run/current-system/sw/bin`).

The selected shell was then executed as a login shell (`-l -c 'env -0'`) for PATH/environment probing.

On systems where a trusted-prefix directory is writable (for example common Homebrew layouts under `/opt/homebrew/bin`) and runtime `$SHELL` can be influenced, this enabled attacker-controlled binary execution in OpenClaw process context.

The fix removes the trusted-prefix executable fallback and now trusts only shells explicitly registered in `/etc/shells`; otherwise it falls back to `/bin/sh`.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `>= 2026.2.22, <= 2026.2.22-2`
- Latest published vulnerable version: `2026.2.22-2`
- Patched versions (released): `>= 2026.2.23`

### Fix Commit(s)
- `ff10fe8b91670044a6bb0cd85deb736a0ec8fb55`

### Release Process Note
This advisory sets `patched_versions` to the released version (`2026.2.23`).
This advisory now reflects released fix version `2026.2.23`.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-p4wh-cr8m-gm6c
- https://nvd.nist.gov/vuln/detail/CVE-2026-22217
- https://github.com/openclaw/openclaw/commit/ff10fe8b91670044a6bb0cd85deb736a0ec8fb55
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-binary-execution-via-shell-environment-variable-trusted-prefix-fallback
