# [C] CVE-2017-9227

## Summary
Severity: Critical
Advisory: CVE-2017-9227
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-24
Source: https://osv.dev/vulnerability/CVE-2017-9227
Type: osv

## Details
An issue was discovered in Oniguruma 6.2.0, as used in Oniguruma-mod in Ruby through 2.4.1 and mbstring in PHP through 7.1.5. A stack out-of-bounds read occurs in mbc_enc_len() during regular expression searching. Invalid handling of reg->dmin in forward_search_range() could result in an invalid pointer dereference, as an out-of-bounds read from a stack buffer.

## References
- http://www.securityfocus.com/bid/100538
- https://access.redhat.com/errata/RHSA-2018:1296
- https://github.com/kkos/oniguruma/commit/9690d3ab1f9bcd2db8cbe1fe3ee4a5da606b8814
- https://github.com/kkos/oniguruma/issues/58
