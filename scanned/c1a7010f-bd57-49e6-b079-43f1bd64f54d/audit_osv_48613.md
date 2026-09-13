# [H] CVE-2018-1000637

## Summary
Severity: High
Advisory: CVE-2018-1000637
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000637
Type: osv

## Details
zutils version prior to version 1.8-pre2 contains a Buffer Overflow vulnerability in zcat that can result in Potential denial of service or arbitrary code execution. This attack appear to be exploitable via the victim openning a crafted compressed file. This vulnerability appears to have been fixed in 1.8-pre2.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00016.html
- https://lists.nongnu.org/archive/html/zutils-bug/2018-08/msg00000.html
- https://bugs.debian.org/904819
