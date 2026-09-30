# [H] Signature Malleabillity in elliptic

## Summary
Severity: High
Advisory: GHSA-vh7m-p724-62c2
CVE: CVE-2020-13822
CWE: CWE-190
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2020-07-29
Source: https://github.com/advisories/GHSA-vh7m-p724-62c2
Type: github-advisory

## Affected
- npm: `elliptic` — affected >=0 <6.5.3

## Details
The Elliptic package before version 6.5.3 for Node.js allows ECDSA signature malleability via variations in encoding, leading '\0' bytes, or integer overflows. This could conceivably have a security-relevant impact if an application relied on a single canonical signature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13822
- https://github.com/indutny/elliptic/issues/226
- https://github.com/indutny/elliptic/commit/856fe4d99fe7b6200556e6400b3bf585b1721bec
- https://github.com/indutny/elliptic
- https://medium.com/%40herman_10687/malleability-attack-why-it-matters-7b5f59fb99a4
- https://medium.com/@herman_10687/malleability-attack-why-it-matters-7b5f59fb99a4
- https://www.npmjs.com/package/elliptic
- https://yondon.blog/2019/01/01/how-not-to-use-ecdsa
