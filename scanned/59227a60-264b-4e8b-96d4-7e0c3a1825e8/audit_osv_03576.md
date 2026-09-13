# [C] ALPINE-CVE-2026-32327

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-32327
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-32327
Type: osv

## Affected
- Alpine:v3.21: `apr-util` — affected >=0 <1.6.4-r0
- Alpine:v3.22: `apr-util` — affected >=0 <1.6.4-r0
- Alpine:v3.23: `apr-util` — affected >=0 <1.6.4-r0
- Alpine:v3.24: `apr-util` — affected >=0 <1.6.4-r0

## Details
A bug in APR-util version 1.6.3 (and earlier) allows a stack recursion attack against any library consumer which parses XML from untrusted sources and uses the apr_xml_quote_elem() function.

Users are recommended to upgrade to version 1.6.4, which fixes this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-32327
