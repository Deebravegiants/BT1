# [H] CVE-2017-14151

## Summary
Severity: High
Advisory: CVE-2017-14151
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/CVE-2017-14151
Type: osv

## Details
An off-by-one error was discovered in opj_tcd_code_block_enc_allocate_data in lib/openjp2/tcd.c in OpenJPEG 2.2.0. The vulnerability causes an out-of-bounds write, which may lead to remote denial of service (heap-based buffer overflow affecting opj_mqc_flush in lib/openjp2/mqc.c and opj_t1_encode_cblk in lib/openjp2/t1.c) or possibly remote code execution.

## References
- http://www.debian.org/security/2017/dsa-4013
- http://www.securityfocus.com/bid/100633
- https://blogs.gentoo.org/ago/2017/08/16/openjpeg-heap-based-buffer-overflow-in-opj_mqc_flush-mqc-c/
- https://github.com/uclouvain/openjpeg/commit/afb308b9ccbe129608c9205cf3bb39bbefad90b9
- https://github.com/uclouvain/openjpeg/issues/982
