# [M] ALPINE-CVE-2022-44792

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-44792
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-11-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-44792
Type: osv

## Affected
- Alpine:v3.14: `net-snmp` — affected >=5.8 <5.9.3-r1
- Alpine:v3.15: `net-snmp` — affected >=5.8 <5.9.3-r1
- Alpine:v3.16: `net-snmp` — affected >=5.8 <5.9.3-r1
- Alpine:v3.17: `net-snmp` — affected >=5.8 <5.9.3-r2
- Alpine:v3.18: `net-snmp` — affected >=5.8 <5.9.3-r2
- Alpine:v3.19: `net-snmp` — affected >=5.8 <5.9.3-r2
- Alpine:v3.20: `net-snmp` — affected >=5.8 <5.9.3-r2
- Alpine:v3.21: `net-snmp` — affected >=5.8 <5.9.3-r2
- Alpine:v3.22: `net-snmp` — affected >=5.8 <5.9.3-r2
- Alpine:v3.23: `net-snmp` — affected >=5.8 <5.9.3-r2
- Alpine:v3.24: `net-snmp` — affected >=5.8 <5.9.3-r2

## Details
handle_ipDefaultTTL in agent/mibgroup/ip-mib/ip_scalars.c in Net-SNMP 5.8 through 5.9.3 has a NULL Pointer Exception bug that can be used by a remote attacker (who has write access) to cause the instance to crash via a crafted UDP packet, resulting in Denial of Service.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-44792
