# [M] CVE-2017-11732

## Summary
Severity: Medium
Advisory: CVE-2017-11732
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-29
Source: https://osv.dev/vulnerability/CVE-2017-11732
Type: osv

## Details
A heap-based buffer overflow vulnerability was found in the function dcputs (called from decompileIMPLEMENTS) in util/decompile.c in Ming 0.4.8, which allows attackers to cause a denial of service via a crafted file.

## References
- http://somevulnsofadlab.blogspot.jp/2017/07/libmingheap-buffer-overflow-in-dcputs.html
- https://github.com/libming/libming/issues/80
- https://lists.debian.org/debian-lts-announce/2018/01/msg00014.html
- https://security.gentoo.org/glsa/201904-24
