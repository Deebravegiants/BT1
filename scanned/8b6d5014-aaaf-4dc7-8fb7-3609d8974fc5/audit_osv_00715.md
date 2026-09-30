# [H] ALPINE-CVE-2017-6891

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-6891
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6891
Type: osv

## Affected
- Alpine:v3.3: `libtasn1` — affected >=0 <4.7-r2
- Alpine:v3.4: `libtasn1` — affected >=0 <4.8-r1
- Alpine:v3.5: `libtasn1` — affected >=0 <4.9-r1
- Alpine:v3.6: `libtasn1` — affected >=0 <4.10-r1

## Details
Two errors in the "asn1_find_node()" function (lib/parser_aux.c) within GnuTLS libtasn1 version 4.10 can be exploited to cause a stacked-based buffer overflow by tricking a user into processing a specially crafted assignments file via the e.g. asn1Coding utility.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6891
