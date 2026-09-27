# [M] ALPINE-CVE-2026-39979

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-39979
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-39979
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.2-r0

## Details
jq is a command-line JSON processor. In commits before 2f09060afab23fe9390cce7cb860b10416e1bf5f, the jv_parse_sized() API in libjq accepts a counted buffer with an explicit length parameter, but its error-handling path formats the input buffer using %s in jv_string_fmt(), which reads until a NUL terminator is found rather than respecting the caller-supplied length. This means that when malformed JSON is passed in a non-NUL-terminated buffer, the error construction logic performs an out-of-bounds read past the end of the buffer. The vulnerability is reachable by any libjq consumer calling jv_parse_sized() with untrusted input, and depending on memory layout, can result in memory disclosure or process termination. The issue has been patched in commit 2f09060afab23fe9390cce7cb860b10416e1bf5f.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-39979
