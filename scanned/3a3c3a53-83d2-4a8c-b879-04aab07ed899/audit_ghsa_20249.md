# [C] Server-Side Request Forgery in kityminder

## Summary
Severity: Critical
Advisory: GHSA-q56h-x9h5-q53c
CVE: CVE-2022-31830
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-06-10
Source: https://github.com/advisories/GHSA-q56h-x9h5-q53c
Type: github-advisory

## Affected
- npm: `kityminder` — affected >=0

## Details
Kity Minder v1.3.5 was discovered to contain a Server-Side Request Forgery (SSRF) via the init function at ImageCapture.class.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31830
- https://github.com/fex-team/kityminder/issues/345
- https://github.com/fex-team/kityminder
