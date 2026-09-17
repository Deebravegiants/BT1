# [M] ALPINE-CVE-2019-20892

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-20892
Ecosystem: Alpine:v3.11, Alpine:v3.12
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-20892
Type: osv

## Affected
- Alpine:v3.11: `net-snmp` — affected >=0 <5.8-r0
- Alpine:v3.12: `net-snmp` — affected >=0 <5.8-r0

## Details
net-snmp before 5.8.1.pre1 has a double free in usm_free_usmStateReference in snmplib/snmpusm.c via an SNMPv3 GetBulk request. NOTE: this affects net-snmp packages shipped to end users by multiple Linux distributions, but might not affect an upstream release.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-20892
