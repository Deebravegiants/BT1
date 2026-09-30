# [M] Feehi CMS host header injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4r4f-jrvw-h727
CVE: CVE-2022-38796
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-15
Source: https://github.com/advisories/GHSA-4r4f-jrvw-h727
Type: github-advisory

## Affected
- Packagist: `feehi/cms` — affected >=0

## Details
A Host Header Injection vulnerability in Feehi CMS 2.1.1 may allow an attacker to spoof a particular header. This can be exploited by abusing password reset emails.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38796
- https://github.com/liufee/cms
- https://www.youtube.com/watch?v=k8dp0FJnSsI
