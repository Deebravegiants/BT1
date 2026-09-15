# [C] Prefix escape

## Summary
Severity: Critical
Advisory: GHSA-qmw8-3v4g-gwj4
CVE: CVE-2021-21321
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-03-03
Source: https://github.com/advisories/GHSA-qmw8-3v4g-gwj4
Type: github-advisory

## Affected
- npm: `fastify-reply-from` — affected >=0 <4.0.2

## Details
### Impact

By crafting a specific URL, it is possible to escape the prefix of the proxied backend service.
If the base url of the proxied server is `/pub/`, a user expect that accessing `/priv` on the target service would not be possible. Unfortunately, it is.

[CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N](https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)

### Patches

A patch have been submitted by Corey Farrell git@cfware.com, the reporter.
All releases after v4.0.2 include the fix.

### Workarounds

There are no workaround available.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [fastify-reply-from](https://github.com/fastify/fastify-reply-from)
* Email us at [hello@matteocollina.com](mailto:hello@matteocollina.com)

## References
- https://github.com/fastify/fastify-reply-from/security/advisories/GHSA-qmw8-3v4g-gwj4
- https://nvd.nist.gov/vuln/detail/CVE-2021-21321
- https://github.com/fastify/fastify-reply-from/commit/dea227dda606900cc01870d08541b4dcc69d3889
- https://www.npmjs.com/package/fastify-reply-from
