# [M] ALPINE-CVE-2026-41256

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-41256
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-41256
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.2-r0

## Details
jq is a command-line JSON processor. In 1.8.1 and earlier, Top-level jq programs loaded from a file with -f are truncated at the first embedded NUL byte on current upstream HEAD. A crafted filter file such as . followed by \x00 and arbitrary suffix compiles and executes as only the prefix before the NUL. This leaves jq with a post-CVE-2026-33948 prefix/full-buffer mismatch on the compilation path even though the JSON parser path has already been fixed.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-41256
