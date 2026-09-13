# [H] Saleor Affected by Denial of Service via Unbounded GraphQL Query Batching

## Summary
Severity: High
Advisory: CVE-2026-33756
Aliases: GHSA-24jw-f244-qfpp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-33756
Type: osv

## Details
Saleor is an e-commerce platform. From 2.0.0 to before 3.23.0a3, 3.22.47, 3.21.54, and 3.20.118, Saleor supports query batching by submitting multiple GraphQL operations in a single HTTP request as a JSON array but wasn't enforcing any upper limit on the number of operations. This allowed an unauthenticated attacker to send a single HTTP request many operations (bypassing the per query complexity limit) to exhaust resources. This vulnerability is fixed in 3.23.0a3, 3.22.47, 3.21.54, and 3.20.118.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33756.json
- https://github.com/saleor/saleor/security/advisories/GHSA-24jw-f244-qfpp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33756
- https://github.com/saleor/saleor/commit/7be352fa8c35875d6e66d36493ca7c14c101bd64
- https://github.com/saleor/saleor/commit/cdb66da97abb7c86939e384914cd8d9194f378e8
- https://github.com/saleor/saleor/commit/d6a94e95bd77f3f733fa66afd1b1ac72e863ca2a
- https://github.com/saleor/saleor/commit/e42aa4d6e588982e78942b033af051c8ec8f43fa
- https://github.com/saleor/saleor/commit/f0371bdd4cafcc841f1a9e7049cead6133bf7464
