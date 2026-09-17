# [M] Bludit uses SHA1 as Password Hashing Algorithm

## Summary
Severity: Medium
Advisory: CVE-2024-24553
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-24553
Type: osv

## Details
Bludit uses the SHA-1 hashing algorithm to compute password hashes. Thus, attackers could determine cleartext passwords with brute-force attacks due to the inherent speed of SHA-1. In addition, the salt that is computed by Bludit is generated with a non-cryptographically secure function.

## References
- https://github.com/bludit/bludit/
- https://www.bludit.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24553.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24553
- https://www.redguard.ch/blog/2024/06/20/security-advisory-bludit/
