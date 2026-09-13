# [H] ALPINE-CVE-2017-12376

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-12376
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12376
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.8: `clamav` — affected >=0 <0.99.3-r0
- Alpine:v3.9: `clamav` — affected >=0 <0.99.3-r0

## Details
ClamAV AntiVirus software versions 0.99.2 and prior contain a vulnerability that could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition or potentially execute arbitrary code on an affected device. The vulnerability is due to improper input validation checking mechanisms when handling Portable Document Format (.pdf) files sent to an affected device. An unauthenticated, remote attacker could exploit this vulnerability by sending a crafted .pdf file to an affected device. This action could cause a handle_pdfname (in pdf.c) buffer overflow when ClamAV scans the malicious file, allowing the attacker to cause a DoS condition or potentially execute arbitrary code.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12376
