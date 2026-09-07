# [M] Cross-site Scripting in django-ajax-utilities

## Summary
Severity: Medium
Advisory: GHSA-p4g9-c9qr-wmg5
CVE: CVE-2017-20182
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-10
Source: https://github.com/advisories/GHSA-p4g9-c9qr-wmg5
Type: github-advisory

## Affected
- PyPI: `django-ajax-utilities` — affected >=0 <1.2.8

## Details
A vulnerability was found in Mobile Vikings Django AJAX Utilities and classified as problematic. This issue affects the function Pagination of the file django_ajax/static/ajax-utilities/js/pagination.js of the component Backslash Handler. The manipulation of the argument url leads to cross site scripting. The attack may be initiated remotely. The patch is on commit  329eb1dd1580ca1f9d4f95bc69939833226515c9 which has been inclused in release 1.2.8. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-222611.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-20182
- https://github.com/mvpoland/django-ajax-utilities/commit/329eb1dd1580ca1f9d4f95bc69939833226515c9
- https://github.com/vikingco/django-ajax-utilities/commit/329eb1dd1580ca1f9d4f95bc69939833226515c9
- https://github.com/mvpoland/django-ajax-utilities
- https://vuldb.com/?ctiid.222611
- https://vuldb.com/?id.222611
