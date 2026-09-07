# [H] Parse Server has a NoSQL injection via token type in password reset and email verification endpoints

## Summary
Severity: High
Advisory: GHSA-vgjh-hmwf-c588
CVE: CVE-2026-30941
CWE: CWE-943
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-vgjh-hmwf-c588
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.5.2-alpha.1
- npm: `parse-server` — affected >=0 <8.6.14

## Details
### Impact

A NoSQL injection vulnerability allows an unauthenticated attacker to inject MongoDB query operators via the `token` field in the password reset and email verification resend endpoints. The `token` value is passed to database queries without type validation and can be used to extract password reset and email verification tokens.

Any Parse Server deployment using MongoDB with email verification or password reset enabled is affected. When `emailVerifyTokenReuseIfValid` is configured, the email verification token can be fully extracted and used to verify a user's email address without inbox access.

### Patches

### Patches

The vulnerability is fixed by adding input type validation at the endpoint level.

### Workarounds

There is no known workaround.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-vgjh-hmwf-c588
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.1
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.14

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-vgjh-hmwf-c588
- https://nvd.nist.gov/vuln/detail/CVE-2026-30941
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.14
- https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.1
