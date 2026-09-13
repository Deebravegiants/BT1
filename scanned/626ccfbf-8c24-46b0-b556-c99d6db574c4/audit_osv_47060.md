# [H] CVE-2015-8836

## Summary
Severity: High
Advisory: CVE-2015-8836
CVSS: 7.3 (CVSS:3.0/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-03-30
Source: https://osv.dev/vulnerability/CVE-2015-8836
Type: osv

## Details
Integer overflow in the isofs_real_read_zf function in isofs.c in FuseISO 20070708 might allow remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a large ZF block size in an ISO file, leading to a heap-based buffer overflow.

## References
- http://www.debian.org/security/2016/dsa-3551
- http://www.openwall.com/lists/oss-security/2015/02/06/7
- http://www.openwall.com/lists/oss-security/2015/02/23/9
- https://bugzilla.redhat.com/show_bug.cgi?id=861358
- https://bugzilla.redhat.com/show_bug.cgi?id=861358
- https://bugzilla.redhat.com/show_bug.cgi?id=861358
- https://bugzilla.redhat.com/show_bug.cgi?id=861358
- https://bugzilla.redhat.com/show_bug.cgi?id=863102
