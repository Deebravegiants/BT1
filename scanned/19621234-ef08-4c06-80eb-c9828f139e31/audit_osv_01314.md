# [M] ALPINE-CVE-2019-10129

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-10129
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10129
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=11.0 <11.3-r0
- Alpine:v3.11: `postgresql` — affected >=11.0 <11.3-r0
- Alpine:v3.12: `postgresql` — affected >=11.0 <11.3-r0
- Alpine:v3.13: `postgresql` — affected >=11.0 <11.3-r0
- Alpine:v3.14: `postgresql` — affected >=11.0 <11.3-r0
- Alpine:v3.6: `postgresql` — affected >=11.0 <9.6.13-r0
- Alpine:v3.7: `postgresql` — affected >=11.0 <10.8-r0
- Alpine:v3.8: `postgresql` — affected >=11.0 <10.8-r0
- Alpine:v3.9: `postgresql` — affected >=11.0 <11.3-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <11.3-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <11.3-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <11.3-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <11.3-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <11.3-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <11.3-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <11.3-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <11.3-r0

## Details
A vulnerability was found in postgresql versions 11.x prior to 11.3. Using a purpose-crafted insert to a partitioned table, an attacker can read arbitrary bytes of server memory. In the default configuration, any user can create a partitioned table suitable for this attack. (Exploit prerequisites are the same as for CVE-2018-1052).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10129
