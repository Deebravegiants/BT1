# [H] SciTokens C++: Relative Path Traversal Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-32725
Aliases: GHSA-rqcx-mc9w-pjxp
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-32725
Type: osv

## Details
SciTokens C++ is a minimal library for creating and using SciTokens from C or C++. Prior to version 1.4.1, scitokens-cpp is vulnerable to an authorization bypass when processing path-based scopes in tokens. The library normalizes the scope path from the token before authorization and collapses ".." path components instead of rejecting them. As a result, an attacker can use parent-directory traversal in the scope claim to broaden the effective authorization beyond the intended directory. This issue has been patched in version 1.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32725.json
- https://github.com/scitokens/scitokens-cpp/security/advisories/GHSA-rqcx-mc9w-pjxp
- https://nvd.nist.gov/vuln/detail/CVE-2026-32725
- https://github.com/scitokens/scitokens-cpp/commit/7951ed809967d88c00c20de414b1ff74df8c3e08
