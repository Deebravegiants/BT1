# [H] OpenBao's cross-namespace lease revocation via legacy sys/revoke path bypasses ACL

## Summary
Severity: High
Advisory: GHSA-v8v8-cm84-m686
CVE: CVE-2026-45808
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-v8v8-cm84-m686
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0 <2.5.4

## Details
# Impact

OpenBao's namespaces provide multi-tenant separation. A tenant who intentionally leaks lease identifiers can have their lease and underlying credential revoked or renewed by a user in another tenant via the legacy, undocumented `sys/revoke` and `sys/renew` endpoints.

# Patch

This will be addressed in v2.5.4.

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-v8v8-cm84-m686
- https://github.com/openbao/openbao/pull/3152
- https://github.com/openbao/openbao/commit/c0495646b41cea0e3f5a1030132e9cf5c2375b5c
- https://github.com/openbao/openbao
- https://github.com/openbao/openbao/releases/tag/v2.5.4
