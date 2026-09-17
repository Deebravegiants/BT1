# [H] c-ares : Use-after-free / double-free in c-ares query-completion handling, remotely triggerable via ares_getaddrinfo() over TCP

## Summary
Severity: High
Advisory: CVE-2026-33630
Aliases: GHSA-6wfj-rwm7-3542
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-33630
Type: osv

## Details
c-ares is an asynchronous resolver library. From ver 1.32.3 until 1.34.7, a use-after-free / double-free in c-ares' query-completion handling. The same flaw — a query's callback being invoked while the query is still linked in the channel's internal lookup structures — is present at multiple points in the resend/finish path (timeout handling, response handling, and query dispatch). If the query, or for ares_getaddrinfo() the owning host_query, is freed as a side effect of that callback, it is then accessed and/or freed a second time. This vulnerability is fixed in ver 1.34.7.

## References
- https://github.com/c-ares/c-ares/releases/tag/v1.34.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33630.json
- https://github.com/c-ares/c-ares/security/advisories/GHSA-6wfj-rwm7-3542
- https://nvd.nist.gov/vuln/detail/CVE-2026-33630
- https://github.com/c-ares/c-ares/commit/1fa3b86a0b8d18fe7b60f3228a01d770feb026bc
- https://github.com/c-ares/c-ares/commit/d823199b688052dcdc1646f2ab4cb8c16b1c644a
- https://github.com/c-ares/c-ares/pull/1237
