# [M] ALPINE-CVE-2018-14055

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-14055
Ecosystem: Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14055
Type: osv

## Affected
- Alpine:v3.5: `znc` — affected >=0 <1.7.1-r0
- Alpine:v3.6: `znc` — affected >=0 <1.7.1-r0
- Alpine:v3.7: `znc` — affected >=0 <1.7.1-r0
- Alpine:v3.8: `znc` — affected >=0 <1.7.1-r0

## Details
ZNC before 1.7.1-rc1 does not properly validate untrusted lines coming from the network, allowing a non-admin user to escalate his privilege and inject rogue values into znc.conf.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14055
