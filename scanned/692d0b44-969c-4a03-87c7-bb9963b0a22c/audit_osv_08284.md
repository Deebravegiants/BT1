# [M] CVE-2016-2116

## Summary
Severity: Medium
Advisory: CVE-2016-2116
CVSS: 5.7 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2016-2116
Type: osv

## Details
Memory leak in the jas_iccprof_createfrombuf function in JasPer 1.900.1 and earlier allows remote attackers to cause a denial of service (memory consumption) via a crafted ICC color profile in a JPEG 2000 image file.

## References
- http://www.openwall.com/lists/oss-security/2016/03/03/12
- http://www.securityfocus.com/bid/84133
- https://bugs.launchpad.net/ubuntu/+source/jasper/+bug/1547865
- http://www.debian.org/security/2016/dsa-3508
- http://www.ubuntu.com/usn/USN-2919-1
- https://access.redhat.com/errata/RHSA-2017:1208
