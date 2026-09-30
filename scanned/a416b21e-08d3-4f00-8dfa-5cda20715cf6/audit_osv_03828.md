# [M] ALPINE-CVE-2026-54679

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-54679
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-54679
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.2-r0

## Details
jq is a command-line JSON processor. Prior to 1.8.2, on 32bit system, jvp_string_append has a chance of integer/multiple overflowing and then causing a massive buffer overrun.  This vulnerability is fixed in 1.8.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-54679
