# [M] CVE-2019-13617

## Summary
Severity: Medium
Advisory: CVE-2019-13617
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-16
Source: https://osv.dev/vulnerability/CVE-2019-13617
Type: osv

## Details
njs through 0.3.3, used in NGINX, has a heap-based buffer over-read in nxt_vsprintf in nxt/nxt_sprintf.c during error handling, as demonstrated by an njs_regexp_literal call that leads to an njs_parser_lexer_error call and then an njs_parser_scope_error call.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15093
- https://github.com/nginx/njs/issues/174
