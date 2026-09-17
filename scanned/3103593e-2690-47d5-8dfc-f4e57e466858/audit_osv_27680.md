# [H] Mailcow Docker Container Exposure to Local Network

## Summary
Severity: High
Advisory: CVE-2024-24760
Aliases: GHSA-gmpj-5xcm-xxx6
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-02
Source: https://osv.dev/vulnerability/CVE-2024-24760
Type: osv

## Details
mailcow is a dockerized email package, with multiple containers linked in one bridged network. A security vulnerability has been identified in mailcow affecting versions < 2024-01c. This vulnerability potentially allows attackers on the same subnet to connect to exposed ports of a Docker container, even when the port is bound to 127.0.0.1. The vulnerability has been addressed by implementing additional iptables/nftables rules. These rules drop packets for Docker containers on ports 3306, 6379, 8983, and 12345, where the input interface is not `br-mailcow` and the output interface is `br-mailcow`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24760.json
- https://github.com/mailcow/mailcow-dockerized/security/advisories/GHSA-gmpj-5xcm-xxx6
- https://nvd.nist.gov/vuln/detail/CVE-2024-24760
- https://github.com/mailcow/mailcow-dockerized/commit/087481ac12bfa5dd715f3630f0b1697be94f7e88
