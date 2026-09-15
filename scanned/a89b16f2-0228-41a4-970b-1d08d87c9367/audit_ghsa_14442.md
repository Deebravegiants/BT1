# [H] Collection.js vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-47pj-q2vm-46xc
CVE: CVE-2023-26113
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-18
Source: https://github.com/advisories/GHSA-47pj-q2vm-46xc
Type: github-advisory

## Affected
- npm: `collection.js` — affected >=0 <6.8.1

## Details
Versions of the package collection.js before 6.8.1 are vulnerable to Prototype Pollution via the `extend` function in `Collection.js/dist/node/iterators/extend.js`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26113
- https://github.com/kobezzza/Collection/issues/27
- https://github.com/kobezzza/Collection/commit/d3d937645f62f37d3115d6aa90bb510fd856e6a2
- https://github.com/kobezzza/Collection
- https://github.com/kobezzza/Collection/blob/be32c48e68f49d3be48a58e929d1ab8ff1d2d19c/dist/node/iterators/extend.js%23L324
- https://github.com/kobezzza/Collection/releases/tag/v6.8.1
- https://security.snyk.io/vuln/SNYK-JS-COLLECTIONJS-3185148
