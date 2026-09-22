# [M] ALPINE-CVE-2021-22918

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-22918
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-07-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22918
Type: osv

## Affected
- Alpine:v3.11: `nodejs` — affected >=0 <12.22.2-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.22.2-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.17.3-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.17.3-r0

## Details
Node.js before 16.4.1, 14.17.2, 12.22.2 is vulnerable to an out-of-bounds read when uv__idna_toascii() is used to convert strings to ASCII. The pointer p is read and increased without checking whether it is beyond pe, with the latter holding a pointer to the end of the buffer. This can lead to information disclosures or crashes. This function can be triggered via uv_getaddrinfo().

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22918
