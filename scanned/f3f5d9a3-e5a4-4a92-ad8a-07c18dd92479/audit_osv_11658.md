# [C] CVE-2017-9226

## Summary
Severity: Critical
Advisory: CVE-2017-9226
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-24
Source: https://osv.dev/vulnerability/CVE-2017-9226
Type: osv

## Details
An issue was discovered in Oniguruma 6.2.0, as used in Oniguruma-mod in Ruby through 2.4.1 and mbstring in PHP through 7.1.5. A heap out-of-bounds write or read occurs in next_state_val() during regular expression compilation. Octal numbers larger than 0xff are not handled correctly in fetch_token() and fetch_token_in_cc(). A malformed regular expression containing an octal number in the form of '\700' would produce an invalid code point value larger than 0xff in next_state_val(), resulting in an out-of-bounds write memory corruption.

## References
- http://www.securityfocus.com/bid/101244
- https://access.redhat.com/errata/RHSA-2018:1296
- https://github.com/kkos/oniguruma/issues/55
- https://github.com/kkos/oniguruma/commit/b4bf968ad52afe14e60a2dc8a95d3555c543353a
- https://github.com/kkos/oniguruma/commit/f015fbdd95f76438cd86366467bb2b39870dd7c6
