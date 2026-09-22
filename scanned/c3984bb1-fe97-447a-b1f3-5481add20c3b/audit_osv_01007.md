# [M] ALPINE-CVE-2018-15378

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-15378
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-15378
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.6: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.7: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.8: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.9: `clamav` — affected >=0 <0.100.2-r0

## Details
A vulnerability in ClamAV versions prior to 0.100.2 could allow an attacker to cause a denial of service (DoS) condition. The vulnerability is due to an error related to the MEW unpacker within the "unmew11()" function (libclamav/mew.c), which can be exploited to trigger an invalid read memory access via a specially crafted EXE file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-15378
