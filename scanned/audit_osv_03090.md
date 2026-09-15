# [M] ALPINE-CVE-2024-41965

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-41965
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 4.2 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-08-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-41965
Type: osv

## Affected
- Alpine:v3.20: `vim` — affected >=0 <9.1.0652-r0
- Alpine:v3.21: `vim` — affected >=0 <9.1.0652-r0
- Alpine:v3.22: `vim` — affected >=0 <9.1.0652-r0
- Alpine:v3.23: `vim` — affected >=0 <9.1.0652-r0

## Details
Vim is an open source command line text editor. double-free in dialog_changed() in Vim < v9.1.0648. When abandoning a buffer, Vim may ask the user what to do with the modified buffer. If the user wants the changed buffer to be saved, Vim may create a new Untitled file, if the buffer did not have a name yet. However, when setting the buffer name to Unnamed, Vim will falsely free a pointer twice, leading to a double-free and possibly later to a heap-use-after-free, which can lead to a crash. The issue has been fixed as of Vim patch v9.1.0648.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-41965
