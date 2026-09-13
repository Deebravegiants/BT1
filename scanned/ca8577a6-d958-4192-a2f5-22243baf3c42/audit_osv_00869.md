# [C] ALPINE-CVE-2018-1000132

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-1000132
Ecosystem: Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-03-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000132
Type: osv

## Affected
- Alpine:v3.5: `mercurial` — affected >=0 <4.5.2-r0
- Alpine:v3.6: `mercurial` — affected >=0 <4.5.2-r0
- Alpine:v3.7: `mercurial` — affected >=0 <4.5.2-r0

## Details
Mercurial version 4.5 and earlier contains a Incorrect Access Control (CWE-285) vulnerability in Protocol server that can result in Unauthorized data access. This attack appear to be exploitable via network connectivity. This vulnerability appears to have been fixed in 4.5.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000132
