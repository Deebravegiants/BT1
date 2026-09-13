# [M] Apache Subversion: mod_dav_svn denial-of-service via control characters in paths

## Summary
Severity: Medium
Advisory: BIT-subversion-2024-46901
Aliases: CVE-2024-46901
Ecosystem: Bitnami
Published: 2024-12-11
Source: https://osv.dev/vulnerability/BIT-subversion-2024-46901
Type: osv

## Affected
- Bitnami: `subversion` — affected >=0 <1.14.5

## Details
Insufficient validation of filenames against control characters in Apache Subversion repositories served via mod_dav_svn allows authenticated users with commit access to commit a corrupted revision, leading to disruption for users of the repository.

All versions of Subversion up to and including Subversion 1.14.4 are affected if serving repositories via mod_dav_svn. Users are recommended to upgrade to version 1.14.5, which fixes this issue.

Repositories served via other access methods are not affected.

## References
- https://subversion.apache.org/security/CVE-2024-46901-advisory.txt
- https://nvd.nist.gov/vuln/detail/CVE-2024-46901
- https://lists.debian.org/debian-lts-announce/2025/04/msg00023.html
