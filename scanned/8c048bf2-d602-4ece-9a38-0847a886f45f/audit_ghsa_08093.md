# [M] bn.js affected by an infinite loop

## Summary
Severity: Medium
Advisory: GHSA-378v-28hj-76wf
CVE: CVE-2026-2739
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-20
Source: https://github.com/advisories/GHSA-378v-28hj-76wf
Type: github-advisory

## Affected
- npm: `bn.js` — affected >=0 <4.12.3
- npm: `bn.js` — affected >=5.0.0 <5.2.3

## Details
This affects versions of the package bn.js before 4.12.3 and 5.2.3. Calling maskn(0) on any BN instance corrupts the internal state, causing toString(), divmod(), and other methods to enter an infinite loop, hanging the process indefinitely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2739
- https://github.com/indutny/bn.js/issues/186
- https://github.com/indutny/bn.js/issues/316
- https://github.com/indutny/bn.js/issues/316#issuecomment-3924217358
- https://github.com/indutny/bn.js/pull/317
- https://github.com/indutny/bn.js/commit/33df26b5771e824f303a79ec6407409376baa64b
- https://gist.github.com/Kr0emer/02370d18328c28b5dd7f9ac880d22a91
- https://github.com/indutny/bn.js
- https://github.com/indutny/bn.js/releases/tag/v5.2.3
- https://security.snyk.io/vuln/SNYK-JS-BNJS-15274301
