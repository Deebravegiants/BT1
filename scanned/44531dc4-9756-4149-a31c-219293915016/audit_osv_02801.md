# [H] ALPINE-CVE-2023-27534

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-27534
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-27534
Type: osv

## Affected
- Alpine:v3.14: `curl` — affected >=7.18.0 <8.0.1-r0
- Alpine:v3.15: `curl` — affected >=7.18.0 <8.0.1-r0
- Alpine:v3.16: `curl` — affected >=7.18.0 <8.0.1-r0
- Alpine:v3.17: `curl` — affected >=7.18.0 <7.88.1-r1
- Alpine:v3.18: `curl` — affected >=7.18.0 <8.0.0-r0
- Alpine:v3.19: `curl` — affected >=7.18.0 <8.0.0-r0
- Alpine:v3.20: `curl` — affected >=7.18.0 <8.0.0-r0
- Alpine:v3.21: `curl` — affected >=7.18.0 <8.0.0-r0
- Alpine:v3.22: `curl` — affected >=7.18.0 <8.0.0-r0
- Alpine:v3.23: `curl` — affected >=7.18.0 <8.0.0-r0
- Alpine:v3.24: `curl` — affected >=7.18.0 <8.0.0-r0

## Details
A path traversal vulnerability exists in curl <8.0.0 SFTP implementation causes the tilde (~) character to be wrongly replaced when used as a prefix in the first path element, in addition to its intended use as the first element to indicate a path relative to the user's home directory. Attackers can exploit this flaw to bypass filtering or execute arbitrary code by crafting a path like /~2/foo while accessing a server with a specific user.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-27534
