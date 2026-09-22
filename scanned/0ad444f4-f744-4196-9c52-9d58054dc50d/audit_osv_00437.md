# [M] ALPINE-CVE-2017-12378

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-12378
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12378
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.8: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.9: `clamav` — affected >=0 <0.99.3-r0

## Details
ClamAV AntiVirus software versions 0.99.2 and prior contain a vulnerability that could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device. The vulnerability is due to improper input validation checking mechanisms of .tar (Tape Archive) files sent to an affected device. A successful exploit could cause a checksum buffer over-read condition when ClamAV scans the malicious .tar file, potentially allowing the attacker to cause a DoS condition on the affected device.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12378
