# [H] ALPINE-CVE-2026-49839

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-49839
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-49839
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.2-r0

## Details
jq is a command-line JSON processor. Prior to 1.8.2,` jq --rawfile` can turn a handled oversized-string error into invalid-state reuse and a real heap out-of-bounds write in assertion-disabled builds. When jv_load_file(raw=1) reads an attacker-controlled file, it repeatedly appends file chunks to the same jv string accumulator. Once jv_string_append_buf() returns jv_invalid_with_msg("String too long"), the raw-file loop does not stop. If the file contains at least one more byte, the next loop iteration appends a new chunk to an object that is already invalid. With assertions enabled this aborts in jvp_string_ptr(). With assertions disabled, the invalid object is interpreted as a string object and ASan reports heap-buffer-overflow. This vulnerability is fixed in 1.8.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-49839
