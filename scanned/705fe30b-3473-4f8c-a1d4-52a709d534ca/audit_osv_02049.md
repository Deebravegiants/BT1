# [H] ALPINE-CVE-2021-1405

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-1405
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-1405
Type: osv

## Affected
- Alpine:v3.11: `clamav` — affected >=0 <0.103.2-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.103.2-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.103.2-r0

## Details
A vulnerability in the email parsing module in Clam AntiVirus (ClamAV) Software version 0.103.1 and all prior versions could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to improper variable initialization that may result in an NULL pointer read. An attacker could exploit this vulnerability by sending a crafted email to an affected device. An exploit could allow the attacker to cause the ClamAV scanning process crash, resulting in a denial of service condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-1405
