# [H] formie's unauthenticated front-end submission editing can overwrite existing submissions

## Summary
Severity: High
Advisory: GHSA-pgxq-p76c-x9cg
CVE: CVE-2026-47266
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-pgxq-p76c-x9cg
Type: github-advisory

## Affected
- Packagist: `verbb/formie` — affected >=3.0.0 <3.1.26
- Packagist: `verbb/formie` — affected >=0 <2.2.21

## Details
### Impact
Unauthenticated users could modify existing submissions by posting a known or guessed submission ID to `formie/submissions/save-submission`.

### Patches
[2.2.21](https://github.com/verbb/formie/releases/tag/2.2.21), [3.1.26](https://github.com/verbb/formie/releases/tag/3.1.26)

### Workarounds
Block unauthenticated access to `actions/formie/submissions/save-submission`, or disable/customize front-end submission editing until patched.

### Credit
formie extends many thanks to:
- Florian (Cyber Security Engineer, arcade solutions ag)
- Contact: [security@arcade.ch](mailto:security@arcade.ch)

## References
- https://github.com/verbb/formie/security/advisories/GHSA-pgxq-p76c-x9cg
- https://nvd.nist.gov/vuln/detail/CVE-2026-47266
- https://github.com/verbb/formie
- https://github.com/verbb/formie/releases/tag/2.2.21
- https://github.com/verbb/formie/releases/tag/3.1.26
