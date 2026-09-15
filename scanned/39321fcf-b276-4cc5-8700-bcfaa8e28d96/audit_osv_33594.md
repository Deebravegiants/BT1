# [M] Unauthenticated Arbitrary File Read via Absolute Path

## Summary
Severity: Medium
Advisory: CVE-2025-46822
Aliases: GHSA-q6mm-cm37-w637
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-05-21
Source: https://osv.dev/vulnerability/CVE-2025-46822
Type: osv

## Details
OsamaTaher/Java-springboot-codebase is a collection of Java and Spring Boot code snippets, applications, and projects. Prior to commit c835c6f7799eacada4c0fc77e0816f250af01ad2, insufficient path traversal mechanisms make absolute path traversal possible. This vulnerability allows unauthorized access to sensitive internal files. Commit c835c6f7799eacada4c0fc77e0816f250af01ad2 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46822.json
- https://github.com/OsamaTaher/Java-springboot-codebase/security/advisories/GHSA-q6mm-cm37-w637
- https://nvd.nist.gov/vuln/detail/CVE-2025-46822
- https://github.com/OsamaTaher/Java-springboot-codebase/commit/c835c6f7799eacada4c0fc77e0816f250af01ad2
