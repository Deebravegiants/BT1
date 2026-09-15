# [H] ALPINE-CVE-2024-6197

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-6197
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-6197
Type: osv

## Affected
- Alpine:v3.17: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.18: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.19: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.20: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.21: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.22: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.23: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.9.0-r0

## Details
libcurl's ASN1 parser has this utf8asn1str() function used for parsing an ASN.1 UTF-8 string. Itcan detect an invalid field and return error. Unfortunately, when doing so it also invokes `free()` on a 4 byte localstack buffer.  Most modern malloc implementations detect this error and immediately abort. Some however accept the input pointer and add that memory to its list of available chunks. This leads to the overwriting of nearby stack memory. The content of the overwrite is decided by the `free()` implementation; likely to be memory pointers and a set of flags.  The most likely outcome of exploting this flaw is a crash, although it cannot be ruled out that more serious results can be had in special circumstances.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-6197
