# [C] ALPINE-CVE-2025-68615

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-68615
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-68615
Type: osv

## Affected
- Alpine:v3.23: `net-snmp` — affected >=0 <5.9.5.2-r0
- Alpine:v3.24: `net-snmp` — affected >=0 <5.9.5.2-r0

## Details
net-snmp is a SNMP application library, tools and daemon. Prior to versions 5.9.5 and 5.10.pre2, a specially crafted packet to an net-snmp snmptrapd daemon can cause a buffer overflow and the daemon to crash. This issue has been patched in versions 5.9.5 and 5.10.pre2.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-68615
