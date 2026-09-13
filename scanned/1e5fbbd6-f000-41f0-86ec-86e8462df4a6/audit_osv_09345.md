# [C] CVE-2016-9538

## Summary
Severity: Critical
Advisory: CVE-2016-9538
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-22
Source: https://osv.dev/vulnerability/CVE-2016-9538
Type: osv

## Details
tools/tiffcrop.c in libtiff 4.0.6 reads an undefined buffer in readContigStripsIntoBuffer() because of a uint16 integer overflow. Reported as MSVR 35100.

## References
- http://www.securityfocus.com/bid/94753
- http://www.debian.org/security/2017/dsa-3762
- http://www.securityfocus.com/bid/94484
- https://github.com/vadz/libtiff/commit/43c0b81a818640429317c80fea1e66771e85024b#diff-c8b4b355f9b5c06d585b23138e1c185f
