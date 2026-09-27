# [H] ALPINE-CVE-2020-3327

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-3327
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-3327
Type: osv

## Affected
- Alpine:v3.11: `clamav` — affected >=0 <0.102.3-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.102.3-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.102.3-r0

## Details
A vulnerability in the ARJ archive parsing module in Clam AntiVirus (ClamAV) Software versions 0.102.2 could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to a heap buffer overflow read. An attacker could exploit this vulnerability by sending a crafted ARJ file to an affected device. An exploit could allow the attacker to cause the ClamAV scanning process crash, resulting in a denial of service condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-3327
