# [M] ALPINE-CVE-2026-43895

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-43895
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-43895
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.2-r0

## Details
jq is a command-line JSON processor. In 1.8.1 and earlier, jq accepts embedded NUL bytes in import paths at the jq-language level, but later resolves those paths through C string operations during module and data-file lookup. This creates a mismatch between the logical import string that policy or audit code may validate and the on-disk path that jq actually opens.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-43895
