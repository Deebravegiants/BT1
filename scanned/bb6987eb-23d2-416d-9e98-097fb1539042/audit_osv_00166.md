# [H] ALPINE-CVE-2016-6328

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-6328
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6328
Type: osv

## Affected
- Alpine:v3.10: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.11: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.12: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.8: `libexif` — affected >=0 <0.6.22-r0
- Alpine:v3.9: `libexif` — affected >=0 <0.6.22-r0

## Details
A vulnerability was found in libexif. An integer overflow when parsing the MNOTE entry data of the input file. This can cause Denial-of-Service (DoS) and Information Disclosure (disclosing some critical heap chunk metadata, even other applications' private data).

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6328
