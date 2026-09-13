# [H] ALPINE-CVE-2018-11803

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-11803
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-11803
Type: osv

## Affected
- Alpine:v3.10: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.11: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.12: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.13: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.14: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.15: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.16: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.17: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.18: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.19: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.20: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.21: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.22: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.23: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.24: `subversion` — affected >=1.10.0 <1.11.1-r0
- Alpine:v3.8: `subversion` — affected >=1.10.0 <1.10.4-r0
- Alpine:v3.9: `subversion` — affected >=1.10.0 <1.11.1-r0

## Details
Subversion's mod_dav_svn Apache HTTPD module versions 1.11.0 and 1.10.0 to 1.10.3 will crash after dereferencing an uninitialized pointer if the client omits the root path in a recursive directory listing operation.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-11803
