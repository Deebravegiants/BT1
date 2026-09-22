# [H] automattic/mongoose vulnerable to Prototype pollution via Schema.path

## Summary
Severity: High
Advisory: GHSA-f825-f98c-gj3g
CVE: CVE-2022-2564
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-07-29
Source: https://github.com/advisories/GHSA-f825-f98c-gj3g
Type: github-advisory

## Affected
- npm: `mongoose` — affected >=6.0.0 <6.4.6
- npm: `mongoose` — affected >=0 <5.13.15

## Details
Mongoose is a MongoDB object modeling tool designed to work in an asynchronous environment. Affected versions of this package are vulnerable to Prototype Pollution. The `Schema.path()` function is vulnerable to prototype pollution when setting the schema object. This vulnerability allows modification of the Object prototype and could be manipulated into a Denial of Service (DoS) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2564
- https://github.com/Automattic/mongoose/commit/99b418941e2fc974199b8e5bd9d382bb50bf680a
- https://github.com/automattic/mongoose/commit/a45cfb6b0ce0067ae9794cfa80f7917e1fb3c6f8
- https://github.com/Automattic/mongoose/blob/51e758541763b6f14569744ced15cc23ab8b50c6/lib/schema.js#L88-L141
- https://github.com/Automattic/mongoose/blob/master/CHANGELOG.md
- https://github.com/Automattic/mongoose/compare/6.4.5...6.4.6
- https://github.com/automattic/mongoose
- https://huntr.dev/bounties/055be524-9296-4b2f-b68d-6d5b810d1ddd
