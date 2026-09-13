# [H] ALPINE-CVE-2017-9229

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9229
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9229
Type: osv

## Affected
- Alpine:v3.4: `php5` — affected >=0 <5.6.31-r0
- Alpine:v3.5: `php5` — affected >=0 <5.6.31-r0

## Details
An issue was discovered in Oniguruma 6.2.0, as used in Oniguruma-mod in Ruby through 2.4.1 and mbstring in PHP through 7.1.5. A SIGSEGV occurs in left_adjust_char_head() during regular expression compilation. Invalid handling of reg->dmax in forward_search_range() could result in an invalid pointer dereference, normally as an immediate denial-of-service condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9229
