# [C] ALPINE-CVE-2017-6519

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-6519
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6519
Type: osv

## Affected
- Alpine:v3.10: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.11: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.12: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.13: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.14: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.15: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.16: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.17: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.18: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.19: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.20: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.21: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.22: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.23: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.24: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.7: `avahi` — affected >=0 <0.6.32-r5
- Alpine:v3.8: `avahi` — affected >=0 <0.7-r2
- Alpine:v3.9: `avahi` — affected >=0 <0.7-r2

## Details
avahi-daemon in Avahi through 0.6.32 and 0.7 inadvertently responds to IPv6 unicast queries with source addresses that are not on-link, which allows remote attackers to cause a denial of service (traffic amplification) and may cause information leakage by obtaining potentially sensitive  information from the responding device via port-5353 UDP packets.  NOTE: this may overlap CVE-2015-2809.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6519
