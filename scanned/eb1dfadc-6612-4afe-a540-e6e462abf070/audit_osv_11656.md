# [C] CVE-2017-9224

## Summary
Severity: Critical
Advisory: CVE-2017-9224
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-24
Source: https://osv.dev/vulnerability/CVE-2017-9224
Type: osv

## Details
An issue was discovered in Oniguruma 6.2.0, as used in Oniguruma-mod in Ruby through 2.4.1 and mbstring in PHP through 7.1.5. A stack out-of-bounds read occurs in match_at() during regular expression searching. A logical error involving order of validation and access in match_at() could result in an out-of-bounds read from a stack buffer.

## References
- http://www.securityfocus.com/bid/101244
- https://access.redhat.com/errata/RHSA-2018:1296
- https://github.com/kkos/oniguruma/issues/57
- https://github.com/kkos/oniguruma/commit/690313a061f7a4fa614ec5cc8368b4f2284e059b
