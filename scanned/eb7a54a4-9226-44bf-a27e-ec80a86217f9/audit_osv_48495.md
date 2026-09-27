# [H] CVE-2017-8373

## Summary
Severity: High
Advisory: CVE-2017-8373
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2017-8373
Type: osv

## Details
The mad_layer_III function in layer3.c in Underbit MAD libmad 0.15.1b allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted audio file.

## References
- https://lists.debian.org/debian-lts-announce/2018/05/msg00011.html
- https://www.debian.org/security/2018/dsa-4192
- https://blogs.gentoo.org/ago/2017/04/30/libmad-heap-based-buffer-overflow-in-mad_layer_iii-layer3-c/
