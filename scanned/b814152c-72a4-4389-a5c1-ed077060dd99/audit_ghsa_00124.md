# [C] Insufficient Entropy in cryptiles

## Summary
Severity: Critical
Advisory: GHSA-rq8g-5pc5-wrhr
CVE: CVE-2018-1000620
CWE: CWE-331
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-09-11
Source: https://github.com/advisories/GHSA-rq8g-5pc5-wrhr
Type: github-advisory

## Affected
- npm: `cryptiles` — affected >=4.0.0 <4.1.2
- npm: `cryptiles` — affected >=3.1.0 <3.1.3

## Details
Versions of `cryptiles` prior to 4.1.2 are vulnerable to Insufficient Entropy. The `randomDigits()` method does not provide sufficient entropy and its generates digits that are not evenly distributed.


## Recommendation

Upgrade to version 4.1.2. The package is deprecated and has been moved to `@hapi/cryptiles` and it is strongly recommended to use the maintained package.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000620
- https://github.com/hapijs/cryptiles/issues/34
- https://github.com/hapijs/cryptiles/issues/35
- https://github.com/hapijs/cryptiles/commit/6bdcd0f6ee8ade96e7b30350bad39ee0c2ef0f9b
- https://github.com/hapijs/cryptiles/commit/9332d4263a32b84e76bf538d7470d01ea63fa047
- https://github.com/hapijs/cryptiles/commit/cb6bd642816e0cb8341d2b3896fd9e7c57e94f56
- https://github.com/hapijs/cryptiles
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/476.json
- https://www.npmjs.com/advisories/1464
- https://www.npmjs.com/advisories/720
