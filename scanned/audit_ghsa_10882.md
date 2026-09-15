# [H] OpenClaw's exec allowlist wrapper analysis did not unwrap env/shell dispatch chains

## Summary
Severity: High
Advisory: GHSA-jj82-76v6-933r
CVE: CVE-2026-27566
CWE: CWE-78, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-jj82-76v6-933r
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
`system.run` exec allowlist analysis treated wrapper binaries as the effective executable and did not fully unwrap `env`/shell-dispatch wrappers.

This allowed wrapper-smuggled payloads (for example `env bash -lc ...`) to satisfy an allowlist entry for the wrapper while executing non-allowlisted commands.

### Impact
On affected versions, an actor who can trigger `system.run` requests under an allowlist policy could bypass intended allowlist restrictions by routing execution through wrapper binaries.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `<= 2026.2.21-2`
- Patched in next release: `2026.2.22` (pre-set below so publish can happen immediately after npm release)

### Fix Commit(s)
- `2b63592be57782c8946e521bc81286933f0f99c7`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`>= 2026.2.22`).

After npm `2026.2.22` is published, this advisory can be published directly without further metadata edits.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jj82-76v6-933r
- https://nvd.nist.gov/vuln/detail/CVE-2026-27566
- https://github.com/openclaw/openclaw/commit/2b63592be57782c8946e521bc81286933f0f99c7
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-allowlist-bypass-via-wrapper-binary-unwrapping-in-system-run
