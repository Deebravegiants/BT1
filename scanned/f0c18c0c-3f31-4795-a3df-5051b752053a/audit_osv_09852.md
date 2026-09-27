# [M] CVE-2017-11705

## Summary
Severity: Medium
Advisory: CVE-2017-11705
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-28
Source: https://osv.dev/vulnerability/CVE-2017-11705
Type: osv

## Details
A memory leak was found in the function parseSWF_SHAPEWITHSTYLE in util/parser.c in Ming 0.4.8, which allows attackers to cause a denial of service via a crafted file.

## References
- http://somevulnsofadlab.blogspot.jp/2017/07/libmingmemory-leak-in.html
- https://github.com/libming/libming/issues/71
