# [H] ALPINE-CVE-2023-22809

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-22809
Ecosystem: Alpine:v3.14, Alpine:v3.15
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-22809
Type: osv

## Affected
- Alpine:v3.14: `sudo` — affected >=1.8.0 <1.9.12_p2-r0
- Alpine:v3.15: `sudo` — affected >=1.8.0 <1.9.12_p2-r0

## Details
In Sudo before 1.9.12p2, the sudoedit (aka -e) feature mishandles extra arguments passed in the user-provided environment variables (SUDO_EDITOR, VISUAL, and EDITOR), allowing a local attacker to append arbitrary entries to the list of files to process. This can lead to privilege escalation. Affected versions are 1.8.0 through 1.9.12.p1. The problem exists because a user-specified editor may contain a "--" argument that defeats a protection mechanism, e.g., an EDITOR='vim -- /path/to/extra/file' value.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-22809
