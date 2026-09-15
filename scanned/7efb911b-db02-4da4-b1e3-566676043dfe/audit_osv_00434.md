# [H] ALPINE-CVE-2017-12375

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-12375
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12375
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.8: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.9: `clamav` — affected >=0 <0.99.3-r0

## Details
The ClamAV AntiVirus software versions 0.99.2 and prior contain a vulnerability that could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device. The vulnerability is due to a lack of input validation checking mechanisms during certain mail parsing functions (the rfc2047 function in mbox.c). An unauthenticated, remote attacker could exploit this vulnerability by sending a crafted email to the affected device. This action could cause a buffer overflow condition when ClamAV scans the malicious email, allowing the attacker to potentially cause a DoS condition on an affected device.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12375
