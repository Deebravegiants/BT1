# [M] @fastify/static vulnerable to route guard bypass via encoded path separators

## Summary
Severity: Medium
Advisory: CVE-2026-6414
Aliases: GHSA-x428-ghpx-8j92
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-6414
Type: osv

## Details
@fastify/static versions 8.0.0 through 9.1.0 decode percent-encoded path separators (%2F) before filesystem resolution, while Fastify's router treats them as literal characters. This mismatch allows attackers to bypass route-based middleware or guards that protect files served by @fastify/static. For example, a route guard on a protected path can be circumvented by encoding the path separator in the URL. Upgrade to @fastify/static 9.1.1 to fix this issue. There are no workarounds.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6414.json
- https://github.com/fastify/fastify-static/security/advisories/GHSA-x428-ghpx-8j92
- https://github.com/fastify/middie/security/advisories/GHSA-cxrg-g7r8-w69p
- https://github.com/honojs/hono/security/advisories/GHSA-q5qw-h33p-qvwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-6414
