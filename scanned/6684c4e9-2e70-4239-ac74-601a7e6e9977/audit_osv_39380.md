# [M] MaxKB: Unsalted MD5 Password Hashing

## Summary
Severity: Medium
Advisory: CVE-2026-45413
Aliases: GHSA-2m4c-mcq5-q8xq
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-45413
Type: osv

## Details
MaxKB is an open-source AI assistant for enterprise. Prior to 2.9.1, user passwords are stored using unsalted MD5 hashes, making them trivially crackable via rainbow tables or GPU-accelerated brute force (hashcat). This vulnerability is fixed in 2.9.1.

## References
- https://github.com/1Panel-dev/MaxKB/security/advisories/GHSA-2m4c-mcq5-q8xq
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45413.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45413
