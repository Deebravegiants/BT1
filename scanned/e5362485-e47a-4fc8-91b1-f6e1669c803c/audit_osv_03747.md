# [M] ALPINE-CVE-2026-44777

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-44777
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-44777
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.2-r0

## Details
jq is a command-line JSON processor. In 1.8.2rc1 and earlier, the ordinary module loader recurses without cycle detection when two
otherwise valid modules include each other.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-44777
