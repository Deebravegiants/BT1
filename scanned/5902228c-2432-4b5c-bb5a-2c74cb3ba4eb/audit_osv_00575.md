# [C] ALPINE-CVE-2017-16931

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-16931
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-16931
Type: osv

## Affected
- Alpine:v3.4: `libxml2` — affected >=0 <2.9.5-r0
- Alpine:v3.5: `libxml2` — affected >=0 <2.9.5-r0
- Alpine:v3.6: `libxml2` — affected >=0 <2.9.5-r0

## Details
parser.c in libxml2 before 2.9.5 mishandles parameter-entity references because the NEXTL macro calls the xmlParserHandlePEReference function in the case of a '%' character in a DTD name.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-16931
