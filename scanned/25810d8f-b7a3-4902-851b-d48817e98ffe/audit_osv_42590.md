# [H] Apache CXF: Revocation bypass in DefaultEncryptingOAuthDataProvider

## Summary
Severity: High
Advisory: CVE-2026-68481
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-68481
Type: osv

## Details
In Apache CXF's DefaultEncryptingOAuthDataProvider, revoked access tokens still decrypt successfully, and TokenIntrospectionService reports active:true. The same applies to refresh tokens. This violates the RFC stipulations that 'The authorization server MUST invalidate the token.' and 'introspection of a revoked token MUST return {"active":false}'. Users are recommended to upgrade to versions 4.2.3 or 4.1.8 or 3.6.12, which fix this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/25
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68481.json
- https://lists.apache.org/thread/88c0h10yjb2b8201o1km3st71fs2zw2b
- https://nvd.nist.gov/vuln/detail/CVE-2026-68481
