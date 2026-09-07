# [M] Cross-Site Request Forgery in MAGMI

## Summary
Severity: Medium
Advisory: GHSA-cv7m-wc7g-7gfp
CVE: CVE-2020-5776
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-cv7m-wc7g-7gfp
Type: github-advisory

## Affected
- Packagist: `dweeves/magmi` — affected >=0

## Details
All versions of MAGMI up to and including version 0.7.24 are vulnerable to CSRF due to the lack of CSRF tokens. RCE (via phpcli command) is possible in the event that a CSRF is leveraged against an existing admin session for MAGMI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5776
- https://www.tenable.com/security/research/tra-2020-51
