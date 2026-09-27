# [M] CVE-2017-11733

## Summary
Severity: Medium
Advisory: CVE-2017-11733
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-29
Source: https://osv.dev/vulnerability/CVE-2017-11733
Type: osv

## Details
A null pointer dereference vulnerability was found in the function stackswap (called from decompileSTACKSWAP) in util/decompile.c in Ming 0.4.8, which allows attackers to cause a denial of service via a crafted file.

## References
- http://somevulnsofadlab.blogspot.jp/2017/07/libmingnull-pointer-dereference-in.html
- https://github.com/libming/libming/issues/78
- https://lists.debian.org/debian-lts-announce/2017/11/msg00022.html
- https://security.gentoo.org/glsa/201904-24
