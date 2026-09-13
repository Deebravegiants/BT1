# [C] CVE-2024-5594

## Summary
Severity: Critical
Advisory: CVE-2024-5594
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2024-5594
Type: osv

## Details
OpenVPN before 2.6.11 does not santize PUSH_REPLY messages properly which an attacker controlling the server can use to inject unexpected arbitrary data ending up in client logs.

## References
- https://community.openvpn.net/openvpn/wiki/CVE-2024-5594
- https://lists.debian.org/debian-lts-announce/2025/03/msg00005.html
- https://www.mail-archive.com/openvpn-users@lists.sourceforge.net/msg07634.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5594.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5594
