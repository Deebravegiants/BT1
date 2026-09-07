# [M] Open Redirect in django-spirit

## Summary
Severity: Medium
Advisory: GHSA-5p9j-w2wx-qx4c
CVE: CVE-2022-0869
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-07
Source: https://github.com/advisories/GHSA-5p9j-w2wx-qx4c
Type: github-advisory

## Affected
- PyPI: `django-spirit` — affected >=0 <0.12.3

## Details
django-spirit prior to version 0.12.3 is vulnerable to open redirect. In the /user/login endpoint, it doesn't check the value of the next parameter when the user is logged in and passes it directly to redirect which result to open redirect. This also affects /user/logout, /user/register, /user/login, /user/resend-activation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0869
- https://github.com/nitely/spirit/commit/8f32f89654d6c30d56e0dd167059d32146fb32ef
- https://github.com/nitely/spirit
- https://huntr.dev/bounties/ed335a88-f68c-4e4d-ac85-f29a51b03342
