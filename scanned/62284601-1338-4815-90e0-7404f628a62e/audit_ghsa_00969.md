# [H] Arbitrary File Overwrite in decompress-zip

## Summary
Severity: High
Advisory: GHSA-73v8-v6g4-vrpm
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-73v8-v6g4-vrpm
Type: github-advisory

## Affected
- npm: `decompress-zip` — affected >=0 <0.2.2
- npm: `decompress-zip` — affected >=0.3.0 <0.3.2

## Details
Vulnerable versions of `decompress-zip` are affected by the Zip-Slip vulnerability, an arbitrary file write vulnerability. The vulnerability occurs because `decompress-zip` does not verify that extracted files do not resolve to targets outside of the extraction root directory.



## Recommendation

For `decompress-zip` 0.2.x upgrade to 0.2.2 or later.
For `decompress-zip` 0.3.x upgrade to 0.3.2 or later.

## References
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/488.json
- https://snyk.io/research/zip-slip-vulnerability
- https://www.npmjs.com/advisories/777
