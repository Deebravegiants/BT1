# [H] OpenClaw's shell startup env injection bypasses system.run allowlist intent (RCE class)

## Summary
Severity: High
Advisory: GHSA-xgf2-vxv2-rrmg
CVE: CVE-2026-32056
CWE: CWE-15, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-xgf2-vxv2-rrmg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
`system.run` environment sanitization allowed shell-startup env overrides (`HOME`, `ZDOTDIR`) that can execute attacker-controlled startup files before allowlist-evaluated command bodies.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `<= 2026.2.21-2` (latest published vulnerable version)
- Planned patched version: `>= 2026.2.22`

### Technical Details
In affected versions:
- Env sanitization blocked many dangerous keys, but not startup-sensitive override keys (`HOME`, `ZDOTDIR`) in host exec env paths.
- Shell-wrapper analysis for allowlist mode models command bodies, but not shell startup side effects.
- Runtime execution used sanitized env, so attacker-provided startup-key overrides could run hidden startup payloads first.

Observed exploit vectors:
- `HOME` + `bash -lc` + malicious `.bash_profile`
- `ZDOTDIR` + `zsh -c` + malicious `.zshenv`

### Fix Commit(s)
- `c2c7114ed39a547ab6276e1e933029b9530ee906`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`>= 2026.2.22`). After the npm release is published, this advisory can be published directly.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xgf2-vxv2-rrmg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32056
- https://github.com/openclaw/openclaw/commit/c2c7114ed39a547ab6276e1e933029b9530ee906
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-remote-code-execution-via-shell-startup-environment-variable-injection-in-system-run
