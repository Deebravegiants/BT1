# [C] ALPINE-CVE-2017-9227

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-9227
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9227
Type: osv

## Affected
- Alpine:v3.4: `php5` — affected >=0 <5.6.31-r0
- Alpine:v3.5: `php5` — affected >=0 <5.6.31-r0

## Details
An issue was discovered in Oniguruma 6.2.0, as used in Oniguruma-mod in Ruby through 2.4.1 and mbstring in PHP through 7.1.5. A stack out-of-bounds read occurs in mbc_enc_len() during regular expression searching. Invalid handling of reg->dmin in forward_search_range() could result in an invalid pointer dereference, as an out-of-bounds read from a stack buffer.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9227
