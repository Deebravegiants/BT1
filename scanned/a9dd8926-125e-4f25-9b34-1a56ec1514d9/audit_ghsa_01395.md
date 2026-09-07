# [H] Cross-Site Scripting in emojione

## Summary
Severity: High
Advisory: GHSA-46m8-42hm-wvvw
CVE: CVE-2016-1000231
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-46m8-42hm-wvvw
Type: github-advisory

## Affected
- npm: `emojione` — affected >=0 <1.3.1

## Details
Affected versions of `emojione` are vulnerable to cross-site scripting when user input is passed into the `toShort()`, `shortnameToImage()`, `unicodeToImage()`, and `toImage()` functions.



## Recommendation

Update to version 1.3.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000231
- https://github.com/Ranks/emojione/issues/61
- https://github.com/joypixels/emojione/commit/613079b16c00e47fb3c44744a67ed88a9295afb1
- https://github.com/Ranks/emojione
- https://github.com/joypixels/emojione/commits/v1.3.1
