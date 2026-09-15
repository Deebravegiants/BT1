# [H] ALPINE-CVE-2020-17525

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-17525
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-17525
Type: osv

## Affected
- Alpine:v3.10: `subversion` — affected >=1.9.0 <1.12.2-r1
- Alpine:v3.11: `subversion` — affected >=1.9.0 <1.12.2-r2
- Alpine:v3.12: `subversion` — affected >=1.9.0 <1.13.0-r3
- Alpine:v3.13: `subversion` — affected >=1.9.0 <1.14.1-r0
- Alpine:v3.14: `subversion` — affected >=1.9.0 <1.14.1-r0
- Alpine:v3.15: `subversion` — affected >=1.9.0 <1.14.1-r0
- Alpine:v3.16: `subversion` — affected >=1.9.0 <1.14.1-r0
- Alpine:v3.17: `subversion` — affected >=1.9.0 <1.14.1-r0
- Alpine:v3.18: `subversion` — affected >=1.9.0 <1.14.1-r0
- Alpine:v3.19: `subversion` — affected >=1.9.0 <1.14.1-r0
- Alpine:v3.20: `subversion` — affected >=1.9.0 <1.14.1-r0
- Alpine:v3.21: `subversion` — affected >=1.9.0 <1.14.1-r0
- Alpine:v3.22: `subversion` — affected >=1.9.0 <1.14.1-r0
- Alpine:v3.23: `subversion` — affected >=1.9.0 <1.14.1-r0
- Alpine:v3.24: `subversion` — affected >=1.9.0 <1.14.1-r0

## Details
Subversion's mod_authz_svn module will crash if the server is using in-repository authz rules with the AuthzSVNReposRelativeAccessFile option and a client sends a request for a non-existing repository URL. This can lead to disruption for users of the service. This issue was fixed in mod_dav_svn+mod_authz_svn servers 1.14.1 and mod_dav_svn+mod_authz_svn servers 1.10.7

## References
- https://security.alpinelinux.org/vuln/CVE-2020-17525
