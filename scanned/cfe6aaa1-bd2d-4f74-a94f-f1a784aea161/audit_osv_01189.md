# [M] ALPINE-CVE-2018-5334

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-5334
Ecosystem: Alpine:v3.5
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-5334
Type: osv

## Affected
- Alpine:v3.5: `wireshark` — affected >=2.2.0 <2.2.12-r0

## Details
In Wireshark 2.4.0 to 2.4.3 and 2.2.0 to 2.2.11, the IxVeriWave file parser could crash. This was addressed in wiretap/vwr.c by correcting the signature timestamp bounds checks.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-5334
