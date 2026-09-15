# [M] ALPINE-CVE-2018-0202

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-0202
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-0202
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.4: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.5: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.6: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.7: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.8: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.9: `clamav` — affected >=0 <0.99.4-r0

## Details
clamscan in ClamAV before 0.99.4 contains a vulnerability that could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device. The vulnerability is due to improper input validation checking mechanisms when handling Portable Document Format (.pdf) files sent to an affected device. An unauthenticated, remote attacker could exploit this vulnerability by sending a crafted .pdf file to an affected device. This action could cause an out-of-bounds read when ClamAV scans the malicious file, allowing the attacker to cause a DoS condition. This concerns pdf_parse_array and pdf_parse_string in libclamav/pdfng.c. Cisco Bug IDs: CSCvh91380, CSCvh91400.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-0202
