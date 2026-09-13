# [C] CVE-2017-14632

## Summary
Severity: Critical
Advisory: CVE-2017-14632
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14632
Type: osv

## Details
Xiph.Org libvorbis 1.3.5 allows Remote Code Execution upon freeing uninitialized memory in the function vorbis_analysis_headerout() in info.c when vi->channels<=0, a similar issue to Mozilla bug 550184.

## References
- https://gitlab.xiph.org/xiph/vorbis/issues/2328
- https://lists.debian.org/debian-lts-announce/2018/04/msg00033.html
- https://usn.ubuntu.com/3569-1/
- https://www.debian.org/security/2018/dsa-4113
