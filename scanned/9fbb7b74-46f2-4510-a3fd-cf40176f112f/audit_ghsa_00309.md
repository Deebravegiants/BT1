# [H] Denial of Service in nes

## Summary
Severity: High
Advisory: GHSA-3pwh-5mmc-mwrx
CVE: CVE-2017-16025
CWE: CWE-400
Ecosystem: npm
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-3pwh-5mmc-mwrx
Type: github-advisory

## Affected
- npm: `nes` — affected >=0 <6.4.1

## Details
Affected versions of `nes` are vulnerable to denial of service when given an invalid `cookie` header, and websocket authentication is set to `cookie`. Submitting an invalid cookie on the websocket upgrade request will cause the node process to throw and exit.


## Recommendation

Update to version 6.4.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16025
- https://github.com/hapijs/nes/issues/171
- https://github.com/hapijs/nes/commit/249ba1755ed6977fbc208463c87364bf884ad655
- https://github.com/advisories/GHSA-3pwh-5mmc-mwrx
- https://www.npmjs.com/advisories/331
