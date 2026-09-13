# [M] CVE-2024-45700

## Summary
Severity: Medium
Advisory: CVE-2024-45700
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2024-45700
Type: osv

## Details
Zabbix server is vulnerable to a DoS vulnerability due to uncontrolled resource exhaustion. An attacker can send specially crafted requests to the server, which will cause the server to allocate an excessive amount of memory and perform CPU-intensive decompression operations, ultimately leading to a service crash.

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00027.html
- https://support.zabbix.com/browse/ZBX-26253
