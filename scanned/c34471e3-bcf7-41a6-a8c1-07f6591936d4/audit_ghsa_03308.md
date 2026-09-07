# [M] Cross-site Scripting in OpenCart

## Summary
Severity: Medium
Advisory: GHSA-36fm-v9wv-56jf
CVE: CVE-2020-10596
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-36fm-v9wv-56jf
Type: github-advisory

## Affected
- Packagist: `opencart/opencart` — affected >=0

## Details
OpenCart 3.0.3.2 allows remote authenticated users to conduct XSS attacks via a crafted filename in the users' image upload section.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10596
- https://github.com/opencart/opencart/issues/7810
- https://github.com/myopencart/ocStore
- http://packetstormsecurity.com/files/157908/OpenCart-3.0.3.2-Cross-Site-Scripting.html
