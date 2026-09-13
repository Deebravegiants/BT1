# [H] CVE-2017-14039

## Summary
Severity: High
Advisory: CVE-2017-14039
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2017-14039
Type: osv

## Details
A heap-based buffer overflow was discovered in the opj_t2_encode_packet function in lib/openjp2/t2.c in OpenJPEG 2.2.0. The vulnerability causes an out-of-bounds write, which may lead to remote denial of service or possibly unspecified other impact.

## References
- http://www.debian.org/security/2017/dsa-4013
- http://www.securityfocus.com/bid/100550
- https://security.gentoo.org/glsa/201710-26
- https://blogs.gentoo.org/ago/2017/08/28/openjpeg-heap-based-buffer-overflow-in-opj_t2_encode_packet-t2-c/
- https://github.com/uclouvain/openjpeg/commit/c535531f03369623b9b833ef41952c62257b507e
- https://github.com/uclouvain/openjpeg/issues/992
