# [M] CVE-2018-18828

## Summary
Severity: Medium
Advisory: CVE-2018-18828
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-30
Source: https://osv.dev/vulnerability/CVE-2018-18828
Type: osv

## Details
There exists a heap-based buffer overflow in vc1_decode_i_block_adv in vc1_block.c in Libav 12.3, which allows attackers to cause a denial-of-service via a crafted aac file.

## References
- https://bugzilla.libav.org/show_bug.cgi?id=1135
