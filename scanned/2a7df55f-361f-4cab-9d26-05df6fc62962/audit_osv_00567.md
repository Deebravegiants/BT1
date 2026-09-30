# [C] ALPINE-CVE-2017-16548

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-16548
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-16548
Type: osv

## Affected
- Alpine:v3.10: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.11: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.12: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.13: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.14: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.15: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.16: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.17: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.18: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.19: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.20: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.21: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.22: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.23: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.24: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.4: `rsync` — affected >=0 <3.1.2-r3
- Alpine:v3.5: `rsync` — affected >=0 <3.1.2-r3
- Alpine:v3.6: `rsync` — affected >=0 <3.1.2-r6
- Alpine:v3.7: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.8: `rsync` — affected >=0 <3.1.2-r7
- Alpine:v3.9: `rsync` — affected >=0 <3.1.2-r7

## Details
The receive_xattr function in xattrs.c in rsync 3.1.2 and 3.1.3-development does not check for a trailing '\0' character in an xattr name, which allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) or possibly have unspecified other impact by sending crafted data to the daemon.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-16548
