# [C] ALPINE-CVE-2025-58050

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-58050
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-08-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-58050
Type: osv

## Affected
- Alpine:v3.22: `pcre2` — affected >=0 <10.46-r0
- Alpine:v3.23: `pcre2` — affected >=0 <10.46-r0
- Alpine:v3.24: `pcre2` — affected >=0 <10.46-r0

## Details
The PCRE2 library is a set of C functions that implement regular expression pattern matching. In version 10.45, a heap-buffer-overflow read vulnerability exists in the PCRE2 regular expression matching engine, specifically within the handling of the (*scs:...) (Scan SubString) verb when combined with (*ACCEPT) in src/pcre2_match.c. This vulnerability may potentially lead to information disclosure if the out-of-bounds data read during the memcmp affects the final match result in a way observable by the attacker. This issue has been resolved in version 10.46.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-58050
