# [M] CVE-2018-20001

## Summary
Severity: Medium
Advisory: CVE-2018-20001
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/CVE-2018-20001
Type: osv

## Details
In Libav 12.3, there is a floating point exception in the range_decode_culshift function (called from range_decode_bits) in libavcodec/apedec.c that will lead to remote denial of service via crafted input.

## References
- https://bugzilla.libav.org/show_bug.cgi?id=1141
