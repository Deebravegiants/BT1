# [H] ALPINE-CVE-2026-53789

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-53789
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53789
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync before 3.5.0 contains an improper path handling vulnerability that allows a malicious sender to expand the scope of --delete operations beyond the intended destination subtree by sending a crafted file list that causes rsync to reclassify implied parent directory entries or treat synthetic paths as the transfer root. Attackers can exploit multiple variants including implied parent reclassification, synthetic root path construction, legacy protocol behavior below version 30, and non-directory root handling to cause the receiver to delete files outside the authorized destination directory.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53789
