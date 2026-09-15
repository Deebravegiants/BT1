# [M] MantisBT has an Authorization Bypass that Allows Uploading Attachments to Private Issues via REST API

## Summary
Severity: Medium
Advisory: GHSA-h4x5-gvx6-3rwc
CVE: CVE-2026-34754
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-h4x5-gvx6-3rwc
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.2

## Details
### Impact
MantisBT allows an authenticated user to upload attachments to private Issues they are not authorized to access.

### Patches
- b262b4d2835b81394d75356dead66e52a6275206

### Workarounds
None.

### Credits
Thanks to Vishal Shukla for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-h4x5-gvx6-3rwc
- https://nvd.nist.gov/vuln/detail/CVE-2026-34754
- https://github.com/mantisbt/mantisbt/commit/b262b4d2835b81394d75356dead66e52a6275206
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=36976
