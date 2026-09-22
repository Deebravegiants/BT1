# [C] CpenClaw's ACPX Windows wrapper shell fallback allowed cwd injection in specific paths

## Summary
Severity: Critical
Advisory: GHSA-6f6j-wx9w-ff4j
CVE: CVE-2026-31999
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-6f6j-wx9w-ff4j
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.2.26 <2026.3.1

## Details
### Summary
On Windows ACPX paths, wrapper resolution for `.cmd`/`.bat` could fall back to shell execution in ways that allowed `cwd` influence to alter execution behavior.

### Impact
In affected Windows ACPX configurations, this could enable command execution integrity loss through cwd-influenced wrapper resolution.

### Fix
Wrapper resolution now prefers explicit PATH/PATHEXT entrypoint resolution and unwrapped Node/EXE execution, with strict fail-closed handling enabled by default for unresolvable wrapper cases.

### Affected and Patched Versions
- Affected: `>= 2026.2.26, < 2026.3.1`
- Patched: `2026.3.1`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6f6j-wx9w-ff4j
- https://nvd.nist.gov/vuln/detail/CVE-2026-31999
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-current-working-directory-injection-via-windows-wrapper-resolution-fallback
