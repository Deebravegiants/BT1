# [M] Wagtail: Improper permission handling when copying snippets

## Summary
Severity: Medium
Advisory: GHSA-x5cx-w6p2-mxf2
CWE: CWE-280
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-x5cx-w6p2-mxf2
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=0 <7.0.9
- PyPI: `wagtail` — affected >=7.1 <7.3.4
- PyPI: `wagtail` — affected >=7.4 <7.4.3
- PyPI: `wagtail` — affected >=8.0rc1 <8.0rc2

## Details
### Impact
A CMS user with "add" permission over a snippet model, but not "change" or "view" permission, could copy an existing snippet that they do not have access to, allowing them to view its contents.

### Patches
Patched versions have been released as Wagtail 7.0.9, 7.3.4, 7.4.3 and 8.0rc2.

### Workarounds
N/A

### Acknowledgements
Many thanks to tinyb0y for reporting this issue.

### For more information
If you have any questions or comments about this advisory:

* Visit Wagtail's [support channels](https://docs.wagtail.org/en/stable/support.html)
* Email us at [security@wagtail.org](mailto:security@wagtail.org) (view our [security policy](https://github.com/wagtail/wagtail/security/policy) for more information).

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-x5cx-w6p2-mxf2
- https://github.com/wagtail/wagtail
