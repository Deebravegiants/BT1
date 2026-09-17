# [M] Saleor has Cross-Account Email Change via Unbound Confirmation Token

## Summary
Severity: Medium
Advisory: CVE-2026-35407
Aliases: GHSA-hwph-9537-mc3p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-35407
Type: osv

## Details
Saleor is an e-commerce platform. From 2.10.0 to before 3.23.0a3, 3.22.47, 3.21.54, and 3.20.118, a business-logic and authorization flaw was found in the account email change workflow, the confirmation flow did not verify that the email change confirmation token was issued for the given authenticated user. As a result, a valid email-change token generated for one account can be replayed while authenticated as a different account. The second account’s email address is then updated to the token's new_email, even though that token was never issued for that account. This vulnerability is fixed in 3.23.0a3, 3.22.47, 3.21.54, and 3.20.118.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35407.json
- https://github.com/saleor/saleor/security/advisories/GHSA-hwph-9537-mc3p
- https://nvd.nist.gov/vuln/detail/CVE-2026-35407
- https://github.com/saleor/saleor/commit/7be352fa8c35875d6e66d36493ca7c14c101bd64
- https://github.com/saleor/saleor/commit/cdb66da97abb7c86939e384914cd8d9194f378e8
- https://github.com/saleor/saleor/commit/d6a94e95bd77f3f733fa66afd1b1ac72e863ca2a
- https://github.com/saleor/saleor/commit/e42aa4d6e588982e78942b033af051c8ec8f43fa
- https://github.com/saleor/saleor/commit/f0371bdd4cafcc841f1a9e7049cead6133bf7464
