# [M] OpenClaw has browser trace/download path symlink escape in temp output handling

## Summary
Severity: Medium
Advisory: GHSA-36h3-7c54-j27r
CVE: CVE-2026-32054
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-36h3-7c54-j27r
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
### Summary
Browser trace/download output path handling allowed symlink-root and symlink-parent escapes from the managed temp root.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.2.24`
- Affected versions: `<= 2026.2.24`
- Planned patched release: `2026.2.25`

### Impact
An attacker with relevant local foothold and ability to influence output paths could route writes outside the intended temp root via symlink traversal, leading to arbitrary file overwrite.

### Fix Commit(s)
- `496a76c03ba85e15ea715e5a583e498ae04d36e3`

### Release Process Note
`patched_versions` is pre-set to the release (`2026.2.25`) so once npm `2026.2.25` is published, the advisory is published.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-36h3-7c54-j27r
- https://nvd.nist.gov/vuln/detail/CVE-2026-32054
- https://github.com/openclaw/openclaw/commit/496a76c03ba85e15ea715e5a583e498ae04d36e3
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-symlink-traversal-in-browser-trace-download-path-handling
