# [H] CVE-2016-4447

## Summary
Severity: High
Advisory: CVE-2016-4447
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-09
Source: https://osv.dev/vulnerability/CVE-2016-4447
Type: osv

## Details
The xmlParseElementDecl function in parser.c in libxml2 before 2.9.4 allows context-dependent attackers to cause a denial of service (heap-based buffer underread and application crash) via a crafted file, involving xmlParseName.

## References
- http://lists.apple.com/archives/security-announce/2016/Jul/msg00000.html
- http://lists.apple.com/archives/security-announce/2016/Jul/msg00001.html
- http://lists.apple.com/archives/security-announce/2016/Jul/msg00002.html
- http://lists.apple.com/archives/security-announce/2016/Jul/msg00005.html
- http://rhn.redhat.com/errata/RHSA-2016-2957.html
- http://www.openwall.com/lists/oss-security/2016/05/25/2
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.securityfocus.com/bid/90864
- http://www.securitytracker.com/id/1036348
- http://www.ubuntu.com/usn/USN-2994-1
- http://xmlsoft.org/news.html
- https://access.redhat.com/errata/RHSA-2016:1292
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05194709
- https://support.apple.com/HT206899
- https://support.apple.com/HT206901
- https://support.apple.com/HT206902
- https://support.apple.com/HT206903
- https://support.apple.com/HT206904
