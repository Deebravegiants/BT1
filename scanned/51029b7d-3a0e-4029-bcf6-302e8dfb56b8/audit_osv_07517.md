# [M] Apache Subversion SVN authz protected copyfrom paths regression

## Summary
Severity: Medium
Advisory: BIT-subversion-2021-28544
Aliases: CVE-2021-28544
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-subversion-2021-28544
Type: osv

## Affected
- Bitnami: `subversion` — affected >=1.10.0 <1.14.2

## Details
Apache Subversion SVN authz protected copyfrom paths regression Subversion servers reveal 'copyfrom' paths that should be hidden according to configured path-based authorization (authz) rules. When a node has been copied from a protected location, users with access to the copy can see the 'copyfrom' path of the original. This also reveals the fact that the node was copied. Only the 'copyfrom' path is revealed; not its contents. Both httpd and svnserve servers are vulnerable.

## References
- http://seclists.org/fulldisclosure/2022/Jul/18
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PZ4ARNGLMGYBKYDX2B7DRBNMF6EH3A6R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YJPMCWCGWBN3QWCDVILWQWPC75RR67LT/
- https://subversion.apache.org/security/CVE-2021-28544-advisory.txt
- https://support.apple.com/kb/HT213345
- https://www.debian.org/security/2022/dsa-5119
- https://nvd.nist.gov/vuln/detail/CVE-2021-28544
