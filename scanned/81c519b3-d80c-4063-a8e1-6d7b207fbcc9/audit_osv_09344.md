# [C] CVE-2016-9537

## Summary
Severity: Critical
Advisory: CVE-2016-9537
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-22
Source: https://osv.dev/vulnerability/CVE-2016-9537
Type: osv

## Details
tools/tiffcrop.c in libtiff 4.0.6 has out-of-bounds write vulnerabilities in buffers. Reported as MSVR 35093, MSVR 35096, and MSVR 35097.

## References
- http://www.securityfocus.com/bid/94746
- http://rhn.redhat.com/errata/RHSA-2017-0225.html
- http://www.debian.org/security/2017/dsa-3762
- http://www.securityfocus.com/bid/94484
- https://github.com/vadz/libtiff/commit/83a4b92815ea04969d494416eaae3d4c6b338e4a#diff-c8b4b355f9b5c06d585b23138e1c185f
