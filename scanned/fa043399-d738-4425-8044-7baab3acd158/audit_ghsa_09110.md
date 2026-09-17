# [M] MantisBT has an authorization bypass that allows reading attachments after losing access to a private issue

## Summary
Severity: Medium
Advisory: GHSA-rmp5-5jj7-gmvf
CVE: CVE-2026-34744
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-rmp5-5jj7-gmvf
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.2

## Details
MantisBT permits a user to list and download their own attachments from an Issue created by another user, even after that Issue becomes private and direct access to it is denied.

### Impact
The loss of confidentiality caused by this vulnerability is minimal, considering that only the attachments that were previously uploaded by the user themselves remains accessible.

### Patches
- de7bdeec36de066235e38a77bf056917d951c84d

### Workarounds
None.

### Credits

Thanks to Vishal Shukla for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-rmp5-5jj7-gmvf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34744
- https://github.com/mantisbt/mantisbt/commit/de7bdeec36de066235e38a77bf056917d951c84d
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=36977
