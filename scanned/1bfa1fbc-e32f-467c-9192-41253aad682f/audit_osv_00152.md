# [C] ALPINE-CVE-2016-6254

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-6254
Ecosystem: Alpine:v3.10, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.9
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2016-08-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6254
Type: osv

## Affected
- Alpine:v3.10: `collectd` — affected >=5.4.0 <5.5.2-r0
- Alpine:v3.4: `collectd` — affected >=5.4.0 <5.5.2-r0
- Alpine:v3.5: `collectd` — affected >=5.4.0 <5.5.2-r0
- Alpine:v3.6: `collectd` — affected >=5.4.0 <5.5.2-r0
- Alpine:v3.9: `collectd` — affected >=5.4.0 <5.5.2-r0

## Details
Heap-based buffer overflow in the parse_packet function in network.c in collectd before 5.4.3 and 5.x before 5.5.2 allows remote attackers to cause a denial of service (daemon crash) or possibly execute arbitrary code via a crafted network packet.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6254
