# [C] ALPINE-CVE-2017-17434

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-17434
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-17434
Type: osv

## Affected
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
- Alpine:v3.7: `rsync` — affected >=0 <3.1.2-r7

## Details
The daemon in rsync 3.1.2, and 3.1.3-development before 2017-12-03, does not check for fnamecmp filenames in the daemon_filter_list data structure (in the recv_files function in receiver.c) and also does not apply the sanitize_paths protection mechanism to pathnames found in "xname follows" strings (in the read_ndx_and_attrs function in rsync.c), which allows remote attackers to bypass intended access restrictions.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-17434
