# [H] DOS and Open Redirect with user input

## Summary
Severity: High
Advisory: GHSA-pgh6-m65r-2rhq
CVE: CVE-2021-22964
CWE: CWE-248, CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-pgh6-m65r-2rhq
Type: github-advisory

## Affected
- npm: `fastify-static` — affected >=4.2.4 <4.4.1

## Details
### Impact

A redirect vulnerability in the `fastify-static` module allows remote attackers to redirect Mozilla Firefox users to arbitrary websites via a double slash `//` followed by a domain: `http://localhost:3000//a//youtube.com/%2e%2e%2f%2e%2e`.

A DOS vulnerability is possible if the URL contains invalid characters `curl --path-as-is "http://localhost:3000//^/.."`

The issue shows up on all the `fastify-static` applications that set `redirect: true` option. By default, it is `false`.

### Patches
The issue has been patched in `fastify-static@4.4.1`

### Workarounds
If updating is not an option, you can sanitize the input URLs using the [`rewriteUrl`](https://www.fastify.io/docs/latest/Server/#rewriteurl) server option.

### References

+ Bug founder: drstrnegth
+ [hackerone Report](https://hackerone.com/reports/1361804)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [fastify-static](https://github.com/fastify/fastify-static)
* Contact the [security team](https://github.com/fastify/fastify/blob/main/SECURITY.md#the-fastify-security-team)

## References
- https://github.com/fastify/fastify-static/security/advisories/GHSA-pgh6-m65r-2rhq
- https://nvd.nist.gov/vuln/detail/CVE-2021-22964
- https://github.com/fastify/fastify-static/commit/c31f17d107cb19a0e96733c80a9abf16c56166d4
- https://hackerone.com/reports/1361804
- https://github.com/fastify/fastify-static
