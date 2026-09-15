# [H] ALPINE-CVE-2017-7401

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7401
Ecosystem: Alpine:v3.5, Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7401
Type: osv

## Affected
- Alpine:v3.5: `collectd` — affected >=0 <5.6.2-r1
- Alpine:v3.6: `collectd` — affected >=0 <5.6.2-r1

## Details
Incorrect interaction of the parse_packet() and parse_part_sign_sha256() functions in network.c in collectd 5.7.1 and earlier allows remote attackers to cause a denial of service (infinite loop) of a collectd instance (configured with "SecurityLevel None" and with empty "AuthFile" options) via a crafted UDP packet.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7401
