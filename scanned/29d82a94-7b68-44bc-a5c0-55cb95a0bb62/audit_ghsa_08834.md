# [C] Electerm: Importing unsafe bookmark data could lead to unsafe operation when clicking local type bookmark

## Summary
Severity: Critical
Advisory: GHSA-jgg9-rw32-44pj
CVE: CVE-2026-45058
CWE: CWE-345, CWE-494, CWE-915, CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-jgg9-rw32-44pj
Type: github-advisory

## Affected
- npm: `electerm` — affected >=0

## Details
### Impact
_Persistent local-pty code execution via imported bookmarks or compromised sync targets. Affects users who import bookmark JSON files or who have electerm sync configured (gist/WebDAV). The attacker can inject `exec*` fields or global config to cause remote code to run when a bookmark is opened or when sync is applied._

### Patches

Not yet

### Workarounds
- Do not import unsafe data

### References
- Report / credit: https://github.com/Curly-Haired-Baboon
- Electerm releases: https://github.com/electerm/electerm/releases

## References
- https://github.com/electerm/electerm/security/advisories/GHSA-jgg9-rw32-44pj
- https://nvd.nist.gov/vuln/detail/CVE-2026-45058
- https://github.com/electerm/electerm
