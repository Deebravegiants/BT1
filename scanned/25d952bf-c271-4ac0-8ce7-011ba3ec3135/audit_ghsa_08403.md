# [M] MantisBT Has Authorization Bypass in Global Profile Creation

## Summary
Severity: Medium
Advisory: GHSA-68w5-w573-q2r8
CVE: CVE-2026-33052
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-68w5-w573-q2r8
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.28.0 <2.28.2

## Details
MantisBT allows a low-privileged authenticated user having *add_profile_threshold* to create a global profile despite not having *manage_global_profile_threshold*, by tampering with the user_id parameter in a valid profile creation request.

### Impact
Authentication bypass

### Patches
- 3f952e68fa864e0e60abc3e84adecf3cfa84c75e

### Workarounds
None

### Credits
Thanks to Vishal Shukla for discovering and responsibly reporting the issues.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-68w5-w573-q2r8
- https://nvd.nist.gov/vuln/detail/CVE-2026-33052
- https://github.com/mantisbt/mantisbt/commit/3f952e68fa864e0e60abc3e84adecf3cfa84c75e
- https://github.com/mantisbt/mantisbt
- https://github.com/mantisbt/mantisbt/releases/tag/release-2.28.2
- https://mantisbt.org/bugs/view.php?id=36974
