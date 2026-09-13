# [M] ALPINE-CVE-2019-18348

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-18348
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.9
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-10-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18348
Type: osv

## Affected
- Alpine:v3.10: `python2` — affected >=0 <2.7.18-r0
- Alpine:v3.11: `python2` — affected >=0 <2.7.18-r0
- Alpine:v3.12: `python2` — affected >=0 <2.7.18-r0
- Alpine:v3.9: `python2` — affected >=0 <2.7.18-r0

## Details
An issue was discovered in urllib2 in Python 2.x through 2.7.17 and urllib in Python 3.x through 3.8.0. CRLF injection is possible if the attacker controls a url parameter, as demonstrated by the first argument to urllib.request.urlopen with \r\n (specifically in the host component of a URL) followed by an HTTP header. This is similar to the CVE-2019-9740 query string issue and the CVE-2019-9947 path string issue. (This is not exploitable when glibc has CVE-2016-10739 fixed.). This is fixed in: v2.7.18, v2.7.18rc1; v3.5.10, v3.5.10rc1; v3.6.11, v3.6.11rc1, v3.6.12; v3.7.8, v3.7.8rc1, v3.7.9; v3.8.3, v3.8.3rc1, v3.8.4, v3.8.4rc1, v3.8.5, v3.8.6, v3.8.6rc1.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18348
