# [C] ALPINE-CVE-2017-16820

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-16820
Ecosystem: Alpine:v3.5, Alpine:v3.6
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-16820
Type: osv

## Affected
- Alpine:v3.5: `collectd` — affected >=0 <5.6.2-r1
- Alpine:v3.6: `collectd` — affected >=0 <5.6.2-r1

## Details
The csnmp_read_table function in snmp.c in the SNMP plugin in collectd before 5.6.3 is susceptible to a double free in a certain error case, which could lead to a crash (or potentially have other impact).

## References
- https://security.alpinelinux.org/vuln/CVE-2017-16820
