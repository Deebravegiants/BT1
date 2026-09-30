# [M] stoatchat before 0.15.0 Missing Authorization via Subscribe

## Summary
Severity: Medium
Advisory: CVE-2026-74869
Aliases: GHSA-jj3j-9qr7-jgfc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74869
Type: osv

## Details
stoatchat before 0.15.0 contains a missing authorization vulnerability in the Subscribe message handler that allows authenticated attackers to enumerate members and monitor profile updates of private servers without membership. Attackers can subscribe to any server's member-update topic by sending a Subscribe message with an arbitrary server ID, receiving live UserUpdate events including display names, avatars, and status changes for members they should not have access to.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74869.json
- https://github.com/stoatchat/stoatchat/security/advisories/GHSA-jj3j-9qr7-jgfc
- https://nvd.nist.gov/vuln/detail/CVE-2026-74869
- https://www.vulncheck.com/advisories/stoatchat-before-missing-authorization-via-subscribe
