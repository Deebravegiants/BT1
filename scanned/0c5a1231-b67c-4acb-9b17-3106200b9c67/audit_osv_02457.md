# [M] ALPINE-CVE-2022-24807

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-24807
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-24807
Type: osv

## Affected
- Alpine:v3.13: `net-snmp` — affected >=0 <5.9.3-r0
- Alpine:v3.14: `net-snmp` — affected >=0 <5.9.3-r0
- Alpine:v3.15: `net-snmp` — affected >=0 <5.9.3-r0
- Alpine:v3.16: `net-snmp` — affected >=0 <5.9.3-r0
- Alpine:v3.17: `net-snmp` — affected >=0 <5.9.3-r0
- Alpine:v3.18: `net-snmp` — affected >=0 <5.9.3-r0
- Alpine:v3.19: `net-snmp` — affected >=0 <5.9.3-r0
- Alpine:v3.20: `net-snmp` — affected >=0 <5.9.3-r0
- Alpine:v3.21: `net-snmp` — affected >=0 <5.9.3-r0
- Alpine:v3.22: `net-snmp` — affected >=0 <5.9.3-r0
- Alpine:v3.23: `net-snmp` — affected >=0 <5.9.3-r0
- Alpine:v3.24: `net-snmp` — affected >=0 <5.9.3-r0

## Details
net-snmp provides various tools relating to the Simple Network Management Protocol. Prior to version 5.9.2, a malformed OID in a SET request to `SNMP-VIEW-BASED-ACM-MIB::vacmAccessTable` can cause an out-of-bounds memory access. A user with read-write credentials can exploit the issue. Version 5.9.2 contains a patch. Users should use strong SNMPv3 credentials and avoid sharing the credentials. Those who must use SNMPv1 or SNMPv2c should use a complex community string and enhance the protection by restricting access to a given IP address range.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-24807
