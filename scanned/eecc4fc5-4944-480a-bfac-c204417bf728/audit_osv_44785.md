# [H] WWBN AVideo Weak PRNG Password Generation via External Login

## Summary
Severity: High
Advisory: CVE-2026-86187
Aliases: GHSA-h3ff-c2qq-pr2g
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86187
Type: osv

## Details
WWBN AVideo generates passwords for external-login accounts using rand() instead of a cryptographic generator, producing only 31-bit integers. Attackers with access to password hashes can recover plaintext passwords in minutes through offline brute-force attacks due to unsalted MD5-based hashing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86187.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-h3ff-c2qq-pr2g
- https://nvd.nist.gov/vuln/detail/CVE-2026-86187
- https://www.vulncheck.com/advisories/wwbn-avideo-weak-prng-password-generation-via-external-login
