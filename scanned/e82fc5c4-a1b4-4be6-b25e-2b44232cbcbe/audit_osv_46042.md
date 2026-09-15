# [C] JLSEC-2026-60

## Summary
Severity: Critical
Advisory: JLSEC-2026-60
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/JLSEC-2026-60
Type: osv

## Affected
- Julia: `PCRE2_jll` — affected >=10.45.0+0 <10.46.0+0

## Details
The PCRE2 library is a set of C functions that implement regular expression pattern matching. In version 10.45, a heap-buffer-overflow read vulnerability exists in the PCRE2 regular expression matching engine, specifically within the handling of the `(*scs:...)` (Scan SubString) verb when combined with `(*ACCEPT)` in `src/pcre2_match.c`. This vulnerability may potentially lead to information disclosure if the out-of-bounds data read during the memcmp affects the final match result in a way observable by the attacker. This issue has been resolved in version 10.46.

## References
- https://github.com/PCRE2Project/pcre2/commit/a141712e5967d448c7ce13090ab530c8e3d82254
- https://github.com/PCRE2Project/pcre2/releases/tag/pcre2-10.46
- https://github.com/PCRE2Project/pcre2/security/advisories/GHSA-c2gv-xgf5-5cc2
