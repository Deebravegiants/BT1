# [M] URL Redirection to Untrusted Site ('Open Redirect') in fastify-static

## Summary
Severity: Medium
Advisory: GHSA-p6vg-p826-qp3v
CVE: CVE-2021-22963
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-05
Source: https://github.com/advisories/GHSA-p6vg-p826-qp3v
Type: github-advisory

## Affected
- npm: `fastify-static` — affected >=0 <4.2.4

## Details
### Impact

A redirect vulnerability in the `fastify-static` module allows remote attackers to redirect Mozilla Firefox users to arbitrary websites via a double slash `//` followed by a domain: `http://localhost:3000//google.com/%2e%2e`.

The issue shows up on all the `fastify-static` applications that set `redirect: true` option. By default, it is `false`.

### Patches
The issue has been patched in `fastify-static@4.2.4`

### Workarounds
If updating is not an option, you can sanitize the input URLs using the [`rewriteUrl`](https://www.fastify.io/docs/latest/Server/#rewriteurl) server option.

### References

+ Bug founder: drstrnegth
+ [hackerone Report](https://hackerone.com/reports/1354255)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [fastify-static](https://github.com/fastify/fastify-static)
* Contact the [security team](https://github.com/fastify/fastify/blob/main/SECURITY.md#the-fastify-security-team)

## References
- https://github.com/fastify/fastify-static/security/advisories/GHSA-p6vg-p826-qp3v
- https://nvd.nist.gov/vuln/detail/CVE-2021-22963
- https://hackerone.com/reports/1354255
- https://github.com/fastify/fastify-static
