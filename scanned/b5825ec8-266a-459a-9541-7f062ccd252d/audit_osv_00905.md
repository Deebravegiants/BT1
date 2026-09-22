# [H] ALPINE-CVE-2018-10906

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-10906
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-10906
Type: osv

## Affected
- Alpine:v3.10: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.11: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.12: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.13: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.14: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.15: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.16: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.17: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.18: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.19: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.20: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.5: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.6: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.7: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.8: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.9: `fuse` — affected >=3.0 <2.9.8-r0
- Alpine:v3.10: `fuse3` — affected >=0 <3.2.5-r0
- Alpine:v3.11: `fuse3` — affected >=0 <3.2.5-r0
- Alpine:v3.12: `fuse3` — affected >=0 <3.2.5-r0
- Alpine:v3.13: `fuse3` — affected >=0 <3.2.5-r0
- Alpine:v3.14: `fuse3` — affected >=0 <3.2.5-r0
- Alpine:v3.15: `fuse3` — affected >=0 <3.2.5-r0
- Alpine:v3.16: `fuse3` — affected >=0 <3.2.5-r0
- Alpine:v3.17: `fuse3` — affected >=0 <3.2.5-r0
- Alpine:v3.18: `fuse3` — affected >=0 <3.2.5-r0

## Details
In fuse before versions 2.9.8 and 3.x before 3.2.5, fusermount is vulnerable to a restriction bypass when SELinux is active. This allows non-root users to mount a FUSE file system with the 'allow_other' mount option regardless of whether 'user_allow_other' is set in the fuse configuration. An attacker may use this flaw to mount a FUSE file system, accessible by other users, and trick them into accessing files on that file system, possibly causing Denial of Service or other unspecified effects.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-10906
