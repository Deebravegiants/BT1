# [H] MantisBT is Vulnerable to XSS leading to account takeover via updating a user's font family preference

## Summary
Severity: High
Advisory: GHSA-j3v9-553h-x28j
CVE: CVE-2026-40596
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:H/VI:L/VA:L/SC:H/SI:H/SA:L (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-j3v9-553h-x28j
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.11.0 <2.28.2

## Details
Any authenticated user can inject arbitrary HTML via updating their account's font family.

### Impact
Cross-site scripting.
The injected payload will be reflected in every MantisBT page.

Leveraging another vulnerability (CSP bypass, see [GHSA-9c3j-xm6v-j7j3](https://github.com/mantisbt/mantisbt/security/advisories/GHSA-9c3j-xm6v-j7j3)), the attacker could achieve account takeover.

### Patches
- 9e8409cdd979eba86ef532756fc47c1d8112d22d

### Workarounds
None

### Credits
Thanks to siunam (Tang Cheuk Hei) for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-9c3j-xm6v-j7j3
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-j3v9-553h-x28j
- https://nvd.nist.gov/vuln/detail/CVE-2026-40596
- https://github.com/mantisbt/mantisbt/commit/9e8409cdd979eba86ef532756fc47c1d8112d22d
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37011
- https://mantisbt.org/bugs/view.php?id=37016
