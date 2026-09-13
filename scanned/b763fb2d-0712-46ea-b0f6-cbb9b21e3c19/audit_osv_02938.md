# [M] ALPINE-CVE-2023-51385

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-51385
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-12-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-51385
Type: osv

## Affected
- Alpine:v3.16: `openssh` — affected >=0 <9.0_p1-r5
- Alpine:v3.17: `openssh` — affected >=0 <9.1_p1-r5
- Alpine:v3.19: `openssh` — affected >=0 <9.6_p1-r0
- Alpine:v3.20: `openssh` — affected >=0 <9.6_p1-r0
- Alpine:v3.21: `openssh` — affected >=0 <9.6_p1-r0
- Alpine:v3.22: `openssh` — affected >=0 <9.6_p1-r0
- Alpine:v3.23: `openssh` — affected >=0 <9.6_p1-r0
- Alpine:v3.24: `openssh` — affected >=0 <9.6_p1-r0

## Details
In ssh in OpenSSH before 9.6, OS command injection might occur if a user name or host name has shell metacharacters, and this name is referenced by an expansion token in certain situations. For example, an untrusted Git repository can have a submodule with shell metacharacters in a user name or host name.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-51385
