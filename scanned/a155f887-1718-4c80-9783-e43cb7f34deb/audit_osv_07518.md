# [H] Apache Subversion mod_dav_svn is vulnerable to memory corruption

## Summary
Severity: High
Advisory: BIT-subversion-2022-24070
Aliases: CVE-2022-24070
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-subversion-2022-24070
Type: osv

## Affected
- Bitnami: `subversion` — affected >=1.14.0 <1.14.2

## Details
Subversion's mod_dav_svn is vulnerable to memory corruption. While looking up path-based authorization rules, mod_dav_svn servers may attempt to use memory which has already been freed. Affected Subversion mod_dav_svn servers 1.10.0 through 1.14.1 (inclusive). Servers that do not use mod_dav_svn are not affected.

## References
- http://seclists.org/fulldisclosure/2022/Jul/18
- https://bz.apache.org/bugzilla/show_bug.cgi?id=65861
- https://cwiki.apache.org/confluence/display/HTTPD/ModuleLife
- https://issues.apache.org/jira/browse/SVN-4880
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PZ4ARNGLMGYBKYDX2B7DRBNMF6EH3A6R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YJPMCWCGWBN3QWCDVILWQWPC75RR67LT/
- https://support.apple.com/kb/HT213345
- https://www.debian.org/security/2022/dsa-5119
- https://nvd.nist.gov/vuln/detail/CVE-2022-24070
