# [M] CVE-2024-56946

## Summary
Severity: Medium
Advisory: CVE-2024-56946
CVSS: 5.3 (CVSS:3.1/AC:L/AV:N/A:L/C:N/I:N/PR:N/S:U/UI:N)
Published: 2025-02-03
Source: https://osv.dev/vulnerability/CVE-2024-56946
Type: osv

## Details
Denial of service in DNS-over-QUIC in Technitium DNS Server <= v13.2.2 allows remote attackers to permanently stop the server from accepting new DNS-over-QUIC connections by triggering unhandled exceptions in listener threads.

## References
- https://github.com/TechnitiumSoftware/DnsServer/blob/master/CHANGELOG.md#version-133
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56946.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56946
- https://github.com/TechnitiumSoftware/DnsServer/commit/a7d1cfb6e836798ef9171677bf8919cf99d9dcb0
