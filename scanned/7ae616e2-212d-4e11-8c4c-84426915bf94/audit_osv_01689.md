# [C] ALPINE-CVE-2019-9948

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-9948
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-03-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9948
Type: osv

## Affected
- Alpine:v3.10: `python2` — affected >=0 <2.7.16-r1
- Alpine:v3.11: `python2` — affected >=0 <2.7.16-r1
- Alpine:v3.12: `python2` — affected >=0 <2.7.16-r1
- Alpine:v3.7: `python2` — affected >=0 <2.7.15-r2
- Alpine:v3.8: `python2` — affected >=0 <2.7.15-r2
- Alpine:v3.9: `python2` — affected >=0 <2.7.16-r1

## Details
urllib in Python 2.x through 2.7.16 supports the local_file: scheme, which makes it easier for remote attackers to bypass protection mechanisms that blacklist file: URIs, as demonstrated by triggering a urllib.urlopen('local_file:///etc/passwd') call.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9948
