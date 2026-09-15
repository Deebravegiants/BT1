# [M] ALPINE-CVE-2019-1787

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-1787
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1787
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.6: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.7: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.8: `clamav` — affected >=0 <0.100.3-r0
- Alpine:v3.9: `clamav` — affected >=0 <0.100.3-r0

## Details
A vulnerability in the Portable Document Format (PDF) scanning functionality of Clam AntiVirus (ClamAV) Software versions 0.101.1 and prior could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device. The vulnerability is due to a lack of proper data handling mechanisms within the device buffer while indexing remaining file data on an affected device. An attacker could exploit this vulnerability by sending crafted PDF files to an affected device. A successful exploit could allow the attacker to cause a heap buffer out-of-bounds read condition, resulting in a crash that could result in a denial of service condition on an affected device.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1787
