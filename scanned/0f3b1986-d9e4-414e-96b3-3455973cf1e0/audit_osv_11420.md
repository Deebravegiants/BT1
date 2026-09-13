# [M] CVE-2017-7697

## Summary
Severity: Medium
Advisory: CVE-2017-7697
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2017-7697
Type: osv

## Details
In libsamplerate before 0.1.9, a buffer over-read occurs in the calc_output_single function in src_sinc.c via a crafted audio file.

## References
- http://www.securityfocus.com/bid/97587
- https://lists.debian.org/debian-lts-announce/2021/12/msg00010.html
- https://github.com/erikd/libsamplerate/issues/11
