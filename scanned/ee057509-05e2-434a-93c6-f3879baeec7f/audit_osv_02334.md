# [H] ALPINE-CVE-2021-43818

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-43818
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L)
Published: 2021-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-43818
Type: osv

## Affected
- Alpine:v3.16: `py3-lxml` — affected >=0 <4.6.5-r0
- Alpine:v3.17: `py3-lxml` — affected >=0 <4.6.5-r0
- Alpine:v3.18: `py3-lxml` — affected >=0 <4.6.5-r0
- Alpine:v3.19: `py3-lxml` — affected >=0 <4.6.5-r0
- Alpine:v3.20: `py3-lxml` — affected >=0 <4.6.5-r0
- Alpine:v3.21: `py3-lxml` — affected >=0 <4.6.5-r0
- Alpine:v3.22: `py3-lxml` — affected >=0 <4.6.5-r0
- Alpine:v3.23: `py3-lxml` — affected >=0 <4.6.5-r0
- Alpine:v3.24: `py3-lxml` — affected >=0 <4.6.5-r0

## Details
lxml is a library for processing XML and HTML in the Python language. Prior to version 4.6.5, the HTML Cleaner in lxml.html lets certain crafted script content pass through, as well as script content in SVG files embedded using data URIs. Users that employ the HTML cleaner in a security relevant context should upgrade to lxml 4.6.5 to receive a patch. There are no known workarounds available.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-43818
