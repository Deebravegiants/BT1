# [H] Heap buffer overflow in T64 codec decompression

## Summary
Severity: High
Advisory: CVE-2023-47118
Aliases: GHSA-g22g-p6q2-x39v
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2023-12-20
Source: https://osv.dev/vulnerability/CVE-2023-47118
Type: osv

## Details
ClickHouse® is an open-source column-oriented database management system that allows generating analytical data reports in real-time. A heap buffer overflow issue was discovered in ClickHouse server. An attacker could send a specially crafted payload to the native interface exposed by default on port 9000/tcp, triggering a bug in the decompression logic of T64 codec that crashes the ClickHouse server process. This attack does not require authentication. Note that this exploit can also be triggered via HTTP protocol, however, the attacker will need a valid credential as the HTTP authentication take places first. This issue has been fixed in version 23.10.2.13-stable, 23.9.4.11-stable, 23.8.6.16-lts and 23.3.16.7-lts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/47xxx/CVE-2023-47118.json
- https://github.com/ClickHouse/ClickHouse/security/advisories/GHSA-g22g-p6q2-x39v
- https://nvd.nist.gov/vuln/detail/CVE-2023-47118
