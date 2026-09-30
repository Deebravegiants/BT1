# [H] SciTokens C++: Sibling-Path Authorization Bypass

## Summary
Severity: High
Advisory: CVE-2026-32726
Aliases: GHSA-q5fm-fgvx-32jq
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-32726
Type: osv

## Details
SciTokens C++ is a minimal library for creating and using SciTokens from C or C++. Prior to version 1.4.1, scitokens-cpp is vulnerable to an authorization bypass in path-based scope validation. The enforcer used a simple string-prefix comparison when checking whether a requested resource path was covered by a token's authorized scope path. Because the check did not require a path-segment boundary, a token scoped to one path could incorrectly authorize access to sibling paths that merely started with the same prefix. This issue has been patched in version 1.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32726.json
- https://github.com/scitokens/scitokens-cpp/security/advisories/GHSA-q5fm-fgvx-32jq
- https://nvd.nist.gov/vuln/detail/CVE-2026-32726
- https://github.com/scitokens/scitokens-cpp/commit/decfe2f00cb9cabbf1e17a3bb2cd4ea1bbbd8a73
