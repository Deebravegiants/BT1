# [C] ALPINE-CVE-2019-9636

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-9636
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9636
Type: osv

## Affected
- Alpine:v3.10: `python2` — affected >=0 <2.7.16-r1
- Alpine:v3.11: `python2` — affected >=0 <2.7.16-r1
- Alpine:v3.12: `python2` — affected >=0 <2.7.16-r1
- Alpine:v3.7: `python2` — affected >=0 <2.7.15-r2
- Alpine:v3.8: `python2` — affected >=0 <2.7.15-r2
- Alpine:v3.9: `python2` — affected >=0 <2.7.16-r1
- Alpine:v3.6: `python3` — affected >=0 <3.6.8-r0
- Alpine:v3.7: `python3` — affected >=0 <3.6.8-r0
- Alpine:v3.8: `python3` — affected >=0 <3.6.8-r0

## Details
Python 2.7.x through 2.7.16 and 3.x through 3.7.2 is affected by: Improper Handling of Unicode Encoding (with an incorrect netloc) during NFKC normalization. The impact is: Information disclosure (credentials, cookies, etc. that are cached against a given hostname). The components are: urllib.parse.urlsplit, urllib.parse.urlparse. The attack vector is: A specially crafted URL could be incorrectly parsed to locate cookies or authentication data and send that information to a different host than when parsed correctly. This is fixed in: v2.7.17, v2.7.17rc1, v2.7.18, v2.7.18rc1; v3.5.10, v3.5.10rc1, v3.5.7, v3.5.8, v3.5.8rc1, v3.5.8rc2, v3.5.9; v3.6.10, v3.6.10rc1, v3.6.11, v3.6.11rc1, v3.6.12, v3.6.9, v3.6.9rc1; v3.7.3, v3.7.3rc1, v3.7.4, v3.7.4rc1, v3.7.4rc2, v3.7.5, v3.7.5rc1, v3.7.6, v3.7.6rc1, v3.7.7, v3.7.7rc1, v3.7.8, v3.7.8rc1, v3.7.9.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9636
