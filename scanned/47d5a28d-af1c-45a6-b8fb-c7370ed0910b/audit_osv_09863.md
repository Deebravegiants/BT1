# [M] CVE-2017-11734

## Summary
Severity: Medium
Advisory: CVE-2017-11734
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-29
Source: https://osv.dev/vulnerability/CVE-2017-11734
Type: osv

## Details
A heap-based buffer over-read was found in the function decompileCALLFUNCTION in util/decompile.c in Ming 0.4.8, which allows attackers to cause a denial of service via a crafted file.

## References
- http://somevulnsofadlab.blogspot.jp/2017/07/libmingheap-buffer-overflow-in_24.html
- https://github.com/libming/libming/issues/83
- https://security.gentoo.org/glsa/201904-24
