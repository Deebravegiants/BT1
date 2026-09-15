# [M] CVE-2018-19761

## Summary
Severity: Medium
Advisory: CVE-2018-19761
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-30
Source: https://osv.dev/vulnerability/CVE-2018-19761
Type: osv

## Details
There is an illegal address access at fromsixel.c (function: sixel_decode_raw_impl) in libsixel 1.8.2 that will cause a denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1649200
