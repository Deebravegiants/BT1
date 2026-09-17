# [M] CVE-2016-6494

## Summary
Severity: Medium
Advisory: CVE-2016-6494
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/CVE-2016-6494
Type: osv

## Details
The client in MongoDB uses world-readable permissions on .dbshell history files, which might allow local users to obtain sensitive information by reading these files.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5MCE2ZLFBNOK3TTWSTXZJQGZVP4EEJDL/
- http://www.openwall.com/lists/oss-security/2016/07/29/4
- http://www.openwall.com/lists/oss-security/2016/07/29/8
- http://www.securityfocus.com/bid/92204
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=832908
- https://bugzilla.redhat.com/show_bug.cgi?id=1362553
- https://jira.mongodb.org/browse/SERVER-25335
- https://github.com/mongodb/mongo/commit/035cf2afc04988b22cb67f4ebfd77e9b344cb6e0
