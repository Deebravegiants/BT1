# [H] CVE-2016-1577

## Summary
Severity: High
Advisory: CVE-2016-1577
CVSS: 7.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2016-1577
Type: osv

## Details
Double free vulnerability in the jas_iccattrval_destroy function in JasPer 1.900.1 and earlier allows remote attackers to cause a denial of service (crash) or possibly execute arbitrary code via a crafted ICC color profile in a JPEG 2000 image file, a different vulnerability than CVE-2014-8137.

## References
- http://www.openwall.com/lists/oss-security/2016/03/03/12
- http://www.securityfocus.com/bid/84133
- https://bugs.launchpad.net/ubuntu/+source/jasper/+bug/1547865
- http://www.debian.org/security/2016/dsa-3508
- http://www.ubuntu.com/usn/USN-2919-1
- https://access.redhat.com/errata/RHSA-2017:1208
