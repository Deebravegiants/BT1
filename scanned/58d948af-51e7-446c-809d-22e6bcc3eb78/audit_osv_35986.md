# [H] @fastify/jwt vulnerable to authorization bypass via global secret overriding the per-request key

## Summary
Severity: High
Advisory: CVE-2026-18500
Aliases: GHSA-j4cx-787j-xjqg
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-18500
Type: osv

## Details
@fastify/jwt is a JSON Web Token plugin for Fastify. In versions before 10.2.2, a per-request verification key passed to request.jwtVerify({ key }) is silently overridden by the plugin's globally configured secret, because the option merge applies the global key last. Applications that use different keys for different authorization domains, for example separate user and admin keys, therefore accept a token signed with the global key on a route that explicitly requires another key. This lets an ordinary authenticated user cross a key-based trust boundary without knowing either secret. The issue is fixed in @fastify/jwt 10.2.2, where an explicit per-call key takes precedence over the global secret. Users should upgrade to 10.2.2.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18500.json
- https://github.com/fastify/fastify-jwt/security/advisories/GHSA-j4cx-787j-xjqg
- https://nvd.nist.gov/vuln/detail/CVE-2026-18500
