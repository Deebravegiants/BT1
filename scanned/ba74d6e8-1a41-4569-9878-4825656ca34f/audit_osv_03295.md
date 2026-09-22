# [H] ALPINE-CVE-2025-46835

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-46835
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-46835
Type: osv

## Affected
- Alpine:v3.19: `git` — affected >=0 <2.43.7-r0
- Alpine:v3.20: `git` — affected >=0 <2.45.4-r0
- Alpine:v3.21: `git` — affected >=0 <2.47.3-r0
- Alpine:v3.22: `git` — affected >=0 <2.49.1-r0
- Alpine:v3.23: `git` — affected >=0 <2.50.1-r0
- Alpine:v3.24: `git` — affected >=0 <2.50.1-r0

## Details
Git GUI allows you to use the Git source control management tools via a GUI. When a user clones an untrusted repository and is tricked into editing a file located in a maliciously named directory in the repository, then Git GUI can create and overwrite files for which the user has write permission. This vulnerability is fixed in 2.43.7, 2.44.4, 2.45.4, 2.46.4, 2.47.3, 2.48.2, 2.49.1, and 2.50.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-46835
