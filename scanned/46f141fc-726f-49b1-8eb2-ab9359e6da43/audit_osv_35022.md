# [M] Auth0 Next.js SDK has Improper Validation of Query Parameters

## Summary
Severity: Medium
Advisory: CVE-2025-67716
Aliases: GHSA-mr6f-h57v-rpj5
CVSS: 5.7 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-12-11
Source: https://osv.dev/vulnerability/CVE-2025-67716
Type: osv

## Details
The Auth0 Next.js SDK is a library for implementing user authentication in Next.js applications. Versions 4.9.0 through 4.12.1 contain an input-validation flaw in the returnTo parameter, which could allow attackers to inject unintended OAuth query parameters into the Auth0 authorization request. Successful exploitation may result in tokens being issued with unintended parameters. This issue is fixed in version 4.13.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67716.json
- https://github.com/auth0/nextjs-auth0/security/advisories/GHSA-mr6f-h57v-rpj5
- https://nvd.nist.gov/vuln/detail/CVE-2025-67716
- https://github.com/auth0/nextjs-auth0/commit/35eb321de3345ccf23e8c0d6f66c9f2f2f57d26c
