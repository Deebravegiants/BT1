# [M] MantisBT: Bugnote Revision Page Leaks Private Issue Metadata After Issue Access Is Revoked

## Summary
Severity: Medium
Advisory: GHSA-crmx-4p49-46m2
CVE: CVE-2026-34970
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-crmx-4p49-46m2
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.2

## Details
MantisBT allows a bugnote author to access the note's Revisions page after losing access to the parent private issue.

### Impact
Disclosure of the private Issue's Id and Summary. The bugnote full revision body remains secure.

### Patches
- 71df1f67e05b2050cd4bd87839e6cc13747cf03f

### Workarounds
None

### Credits 
Thanks to Vishal Shukla for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-crmx-4p49-46m2
- https://nvd.nist.gov/vuln/detail/CVE-2026-34970
- https://github.com/mantisbt/mantisbt/commit/71df1f67e05b2050cd4bd87839e6cc13747cf03f
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=36978
