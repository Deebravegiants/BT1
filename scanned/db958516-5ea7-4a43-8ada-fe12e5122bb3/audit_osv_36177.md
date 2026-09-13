# [M] axios4go's Race Condition in Shared HTTP Client Allows Proxy Configuration Leak

## Summary
Severity: Medium
Advisory: CVE-2026-21697
Aliases: GHSA-cmj9-27wj-7x47
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21697
Type: osv

## Details
axios4go is a Go HTTP client library. Prior to version 0.6.4, a race condition vulnerability exists in the shared HTTP client configuration. The global `defaultClient` is mutated during request execution without synchronization, directly modifying the shared `http.Client`'s `Transport`, `Timeout`, and `CheckRedirect` properties. Impacted applications include that that use axios4go with concurrent requests (multiple goroutines, `GetAsync`, `PostAsync`, etc.), those where different requests use different proxy configurations, and those that handle sensitive data (authentication credentials, tokens, API keys). Version 0.6.4 fixes this issue.

## References
- https://github.com/rezmoss/axios4go/releases/tag/v0.6.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21697.json
- https://github.com/rezmoss/axios4go/security/advisories/GHSA-cmj9-27wj-7x47
- https://nvd.nist.gov/vuln/detail/CVE-2026-21697
- https://github.com/rezmoss/axios4go/commit/b651604c64e66a115ab90cdab358b0181d74a842
