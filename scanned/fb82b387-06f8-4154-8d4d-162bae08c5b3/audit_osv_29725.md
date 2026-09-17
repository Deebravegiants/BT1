# [M] Suricata defrag: off by one can lead to policy bypass

## Summary
Severity: Medium
Advisory: CVE-2024-45796
Aliases: GHSA-mf6r-3xp2-v7xg
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-10-16
Source: https://osv.dev/vulnerability/CVE-2024-45796
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to version 7.0.7, a logic error during fragment reassembly can lead to failed reassembly for valid traffic. An attacker could craft packets to trigger this behavior.This issue has been addressed in 7.0.7.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00029.html
- https://redmine.openinfosecfoundation.org/issues/7067
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45796.json
- https://github.com/OISF/suricata/security/advisories/GHSA-mf6r-3xp2-v7xg
- https://nvd.nist.gov/vuln/detail/CVE-2024-45796
