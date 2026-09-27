# [M] CVE-2017-11703

## Summary
Severity: Medium
Advisory: CVE-2017-11703
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-28
Source: https://osv.dev/vulnerability/CVE-2017-11703
Type: osv

## Details
A memory leak vulnerability was found in the function parseSWF_DOACTION in util/parser.c in Ming 0.4.8, which allows attackers to cause a denial of service via a crafted file.

## References
- http://somevulnsofadlab.blogspot.jp/2017/07/libmingmemory-leak-in-parseswfdoaction.html
- https://github.com/libming/libming/issues/72
