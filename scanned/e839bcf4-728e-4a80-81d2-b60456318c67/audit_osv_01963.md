# [M] ALPINE-CVE-2020-3350

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-3350
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-06-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-3350
Type: osv

## Affected
- Alpine:v3.11: `clamav` — affected >=0 <0.102.4-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.102.4-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.102.4-r0

## Details
A vulnerability in the endpoint software of Cisco AMP for Endpoints and Clam AntiVirus could allow an authenticated, local attacker to cause the running software to delete arbitrary files on the system. The vulnerability is due to a race condition that could occur when scanning malicious files. An attacker with local shell access could exploit this vulnerability by executing a script that could trigger the race condition. A successful exploit could allow the attacker to delete arbitrary files on the system that the attacker would not normally have privileges to delete, producing system instability or causing the endpoint software to stop working.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-3350
