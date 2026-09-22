# [H] CVE-2016-9391

## Summary
Severity: High
Advisory: CVE-2016-9391
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-9391
Type: osv

## Details
The jpc_bitstream_getbits function in jpc_bs.c in JasPer before 2.0.10 allows remote attackers to cause a denial of service (assertion failure) via a very large integer.

## References
- https://usn.ubuntu.com/3693-1/
- http://www.securityfocus.com/bid/94371
- https://access.redhat.com/errata/RHSA-2017:1208
- http://www.openwall.com/lists/oss-security/2016/11/17/1
- https://blogs.gentoo.org/ago/2016/11/16/jasper-multiple-assertion-failure
- https://bugzilla.redhat.com/show_bug.cgi?id=1396967
- https://github.com/mdadams/jasper/commit/1e84674d95353c64e5c4c0e7232ae86fd6ea813b
