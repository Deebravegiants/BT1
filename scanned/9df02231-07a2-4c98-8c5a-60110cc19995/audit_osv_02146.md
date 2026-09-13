# [M] ALPINE-CVE-2021-28153

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-28153
Ecosystem: Alpine:v3.13
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-03-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28153
Type: osv

## Affected
- Alpine:v3.13: `glib` — affected >=0 <2.66.6-r0

## Details
An issue was discovered in GNOME GLib before 2.66.8. When g_file_replace() is used with G_FILE_CREATE_REPLACE_DESTINATION to replace a path that is a dangling symlink, it incorrectly also creates the target of the symlink as an empty file, which could conceivably have security relevance if the symlink is attacker-controlled. (If the path is a symlink to a file that already exists, then the contents of that file correctly remain unchanged.)

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28153
