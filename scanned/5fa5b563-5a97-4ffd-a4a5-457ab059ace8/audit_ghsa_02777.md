# [M] Cross-site scripting in application/controllers/dropbox.php in JustWriting

## Summary
Severity: Medium
Advisory: GHSA-gxmc-5wj3-jx64
CVE: CVE-2021-41467
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-04
Source: https://github.com/advisories/GHSA-gxmc-5wj3-jx64
Type: github-advisory

## Affected
- Packagist: `hjue/justwriting` — affected >=0

## Details
Cross-site scripting (XSS) vulnerability in application/controllers/dropbox.php in JustWriting 1.0.0 and below allow remote attackers to inject arbitrary web script or HTML via the challenge parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41467
- https://github.com/hjue/JustWriting/issues/106
- https://github.com/hjue/JustWriting
