# [C] CVE-2017-9228

## Summary
Severity: Critical
Advisory: CVE-2017-9228
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-24
Source: https://osv.dev/vulnerability/CVE-2017-9228
Type: osv

## Details
An issue was discovered in Oniguruma 6.2.0, as used in Oniguruma-mod in Ruby through 2.4.1 and mbstring in PHP through 7.1.5. A heap out-of-bounds write occurs in bitset_set_range() during regular expression compilation due to an uninitialized variable from an incorrect state transition. An incorrect state transition in parse_char_class() could create an execution path that leaves a critical local variable uninitialized until it's used as an index, resulting in an out-of-bounds write memory corruption.

## References
- https://access.redhat.com/errata/RHSA-2018:1296
- https://github.com/kkos/oniguruma/issues/60
- https://github.com/kkos/oniguruma/commit/3b63d12038c8d8fc278e81c942fa9bec7c704c8b
