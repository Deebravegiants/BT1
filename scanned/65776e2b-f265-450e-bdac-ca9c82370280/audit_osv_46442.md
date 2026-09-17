# [C] CVE-2010-5325

## Summary
Severity: Critical
Advisory: CVE-2010-5325
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-15
Source: https://osv.dev/vulnerability/CVE-2010-5325
Type: osv

## Details
Heap-based buffer overflow in the unhtmlify function in foomatic-rip in foomatic-filters before 4.0.6 allows remote attackers to cause a denial of service (memory corruption and crash) or possibly execute arbitrary code via a long job title.

## References
- http://bzr.linuxfoundation.org/loggerhead/openprinting/foomatic-4.0/foomatic-filters/annotate/head:/ChangeLog
- http://rhn.redhat.com/errata/RHSA-2016-0491.html
- http://www.openwall.com/lists/oss-security/2016/02/15/1
- http://www.openwall.com/lists/oss-security/2016/02/15/7
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://bzr.linuxfoundation.org/loggerhead/openprinting/foomatic-4.0/foomatic-filters/annotate/head:/ChangeLog
- https://bugzilla.redhat.com/show_bug.cgi?id=1218297
- https://bugs.linuxfoundation.org/show_bug.cgi?id=515
