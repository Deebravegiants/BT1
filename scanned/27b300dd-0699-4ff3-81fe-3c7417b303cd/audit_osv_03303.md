# [H] ALPINE-CVE-2025-48060

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-48060
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-48060
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.0-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.0-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.0-r0

## Details
jq is a command-line JSON processor. In versions up to and including 1.7.1, a heap-buffer-overflow is present in function `jv_string_vfmt` in the jq_fuzz_execute harness from oss-fuzz. This crash happens on file jv.c, line 1456 `void* p = malloc(sz);`. As of time of publication, no patched versions are available.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-48060
