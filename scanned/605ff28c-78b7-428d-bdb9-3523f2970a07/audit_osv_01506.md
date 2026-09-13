# [M] ALPINE-CVE-2019-1788

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-1788
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1788
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
A vulnerability in the Object Linking & Embedding (OLE2) file scanning functionality of Clam AntiVirus (ClamAV) Software versions 0.101.1 and prior could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to a lack of proper input and validation checking mechanisms for OLE2 files sent an affected device. An attacker could exploit this vulnerability by sending malformed OLE2 files to the device running an affected version ClamAV Software. An exploit could allow the attacker to cause an out-of-bounds write condition, resulting in a crash that could result in a denial of service condition on an affected device.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1788
