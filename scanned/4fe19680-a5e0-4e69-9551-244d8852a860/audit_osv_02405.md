# [H] ALPINE-CVE-2022-20792

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-20792
Ecosystem: Alpine:v3.12, Alpine:v3.13
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-08-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-20792
Type: osv

## Affected
- Alpine:v3.12: `clamav` — affected >=0.104.0 <0.103.6-r0
- Alpine:v3.13: `clamav` — affected >=0.104.0 <0.103.6-r0

## Details
A vulnerability in the regex module used by the signature database load module of Clam AntiVirus (ClamAV) versions 0.104.0 through 0.104.2 and LTS version 0.103.5 and prior versions could allow an authenticated, local attacker to crash ClamAV at database load time, and possibly gain code execution. The vulnerability is due to improper bounds checking that may result in a multi-byte heap buffer overwflow write. An attacker could exploit this vulnerability by placing a crafted CDB ClamAV signature database file in the ClamAV database directory. An exploit could allow the attacker to run code as the clamav user.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-20792
