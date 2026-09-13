# [H] CVE-2017-11684

## Summary
Severity: High
Advisory: CVE-2017-11684
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-27
Source: https://osv.dev/vulnerability/CVE-2017-11684
Type: osv

## Details
There is an illegal address access in the build_table function in libavcodec/bitstream.c of Libav 12.1 that will lead to remote denial of service via crafted input.

## References
- http://www.securityfocus.com/bid/99980
- https://bugzilla.libav.org/show_bug.cgi?id=1073
