# [C] ALPINE-CVE-2017-1000116

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-1000116
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-1000116
Type: osv

## Affected
- Alpine:v3.3: `mercurial` — affected >=0 <4.3.1-r0
- Alpine:v3.4: `mercurial` — affected >=0 <4.3.1-r0
- Alpine:v3.5: `mercurial` — affected >=0 <4.3.1-r0
- Alpine:v3.6: `mercurial` — affected >=0 <4.3.1-r0

## Details
Mercurial prior to 4.3 did not adequately sanitize hostnames passed to ssh, leading to possible shell-injection attacks.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-1000116
