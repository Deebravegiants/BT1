# [M] FreshRSS has an authentication bypass due to truncated bcrypt hash [edge branch]

## Summary
Severity: Medium
Advisory: CVE-2025-68402
Aliases: GHSA-pcq9-mq6m-mvmp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-09
Source: https://osv.dev/vulnerability/CVE-2025-68402
Type: osv

## Details
FreshRSS is a free, self-hostable RSS aggregator. From 57e1a37 - 00f2f04, the lengths of the nonce was changed from 40 chars to 64. password_verify() is currently being called with a constructed string (SHA-256 nonce + part of a bcrypt hash) instead of the raw user password. Due to bcrypt’s 72-byte input truncation, this causes password verification to succeed even when the user enters an incorrect password. This vulnerability is fixed in 1.27.2-dev (476e57b). The issue was only present in the edge branch and never in a stable release.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68402.json
- https://github.com/FreshRSS/FreshRSS/security/advisories/GHSA-pcq9-mq6m-mvmp
- https://nvd.nist.gov/vuln/detail/CVE-2025-68402
- https://github.com/FreshRSS/FreshRSS/commit/476e57b04646416e24e24c56133c9fadf9e52b95
- https://github.com/FreshRSS/FreshRSS/pull/8061
- https://github.com/FreshRSS/FreshRSS/pull/8320
