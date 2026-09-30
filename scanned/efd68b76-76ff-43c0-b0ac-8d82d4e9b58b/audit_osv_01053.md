# [C] ALPINE-CVE-2018-17141

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-17141
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-17141
Type: osv

## Affected
- Alpine:v3.10: `hylafax` — affected >=0 <6.0.6-r5
- Alpine:v3.11: `hylafax` — affected >=0 <6.0.6-r5
- Alpine:v3.12: `hylafax` — affected >=0 <6.0.6-r5
- Alpine:v3.13: `hylafax` — affected >=0 <6.0.6-r5
- Alpine:v3.14: `hylafax` — affected >=0 <6.0.6-r5
- Alpine:v3.15: `hylafax` — affected >=0 <6.0.6-r5
- Alpine:v3.16: `hylafax` — affected >=0 <6.0.6-r5
- Alpine:v3.17: `hylafax` — affected >=0 <6.0.6-r5
- Alpine:v3.18: `hylafax` — affected >=0 <6.0.6-r5
- Alpine:v3.19: `hylafax` — affected >=0 <6.0.6-r5
- Alpine:v3.20: `hylafax` — affected >=0 <6.0.6-r5
- Alpine:v3.5: `hylafax` — affected >=0 <6.0.6-r4
- Alpine:v3.6: `hylafax` — affected >=0 <6.0.6-r5
- Alpine:v3.7: `hylafax` — affected >=0 <6.0.6-r4
- Alpine:v3.8: `hylafax` — affected >=0 <6.0.6-r5
- Alpine:v3.9: `hylafax` — affected >=0 <6.0.6-r5

## Details
HylaFAX 6.0.6 and HylaFAX+ 5.6.0 allow remote attackers to execute arbitrary code via a dial-in session that provides a FAX page with the JPEG bit enabled, which is mishandled in FaxModem::writeECMData() in the faxd/CopyQuality.c++ file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-17141
