# [H] Apache CXF: The authorization code hash (c_hash) is not enforced for the hybrid OIDC flow

## Summary
Severity: High
Advisory: CVE-2026-57817
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-57817
Type: osv

## Details
The OpenID Connect Core 1.0 specification mandates that the RP MUST validate the `c_hash` parameter when operating in the Hybrid Flow. If an Apache CXF RP is integrated with a non-compliant or misconfigured Identity Provider (IdP) that omits the `c_hash`, the RP becomes vulnerable to Authorization Code Substitution/Injection attacks. Users are recommended to upgrade to versions 4.2.3 or 4.1.8 or 3.6.12, which fix this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/19
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57817.json
- https://lists.apache.org/thread/pj63c3pf7kkp1xhr53do704fwj3t3htn
- https://nvd.nist.gov/vuln/detail/CVE-2026-57817
