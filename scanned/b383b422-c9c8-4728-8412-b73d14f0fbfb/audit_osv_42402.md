# [C] Apache CXF: DefaultEncryptingCodeDataProvider allows unlimited authorization code replay

## Summary
Severity: Critical
Advisory: CVE-2026-68079
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-68079
Type: osv

## Details
In Apache CXF's DefaultEncryptingCodeDataProvider, a captured authorization code can be redeemed an unlimited number of times due to a flaw in the implementation of the removeCodeGrant functionality. This violates the RFC requirement that "The authorization code MUST NOT be used more than once." Users are recommended to upgrade to versions 4.2.3 or 4.1.8 or 3.6.12, which fix this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/24
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68079.json
- https://lists.apache.org/thread/6m06gdqz4rxhy9g90qz9lyqx2gqmf13o
- https://nvd.nist.gov/vuln/detail/CVE-2026-68079
