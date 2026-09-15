# [M] ALPINE-CVE-2016-2125

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-2125
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2125
Type: osv

## Affected
- Alpine:v3.2: `samba` — affected >=3.0.25 <4.2.14-r1
- Alpine:v3.3: `samba` — affected >=3.0.25 <4.2.14-r1
- Alpine:v3.4: `samba` — affected >=3.0.25 <4.4.5-r2

## Details
It was found that Samba before versions 4.5.3, 4.4.8, 4.3.13 always requested forwardable tickets when using Kerberos authentication. A service to which Samba authenticated using Kerberos could subsequently use the ticket to impersonate Samba to other services or domain users.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2125
