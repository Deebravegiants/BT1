# [H] Path Traversal in http-live-simulator

## Summary
Severity: High
Advisory: GHSA-7c9w-qmrq-ff8r
CVE: CVE-2018-16479
CWE: CWE-22
Ecosystem: npm
Published: 2019-02-07
Source: https://github.com/advisories/GHSA-7c9w-qmrq-ff8r
Type: github-advisory

## Affected
- npm: `http-live-simulator` — affected >=0 <1.0.7

## Details
Versions of `http-live-simulator` prior to 1.0.7 are vulnerable to Path Traversal.  Due to insufficient input sanitization, attackers can access server files by using relative paths. For example: `curl --path-as-is http://localhost:8080//../../../../etc/passwd`.


## Recommendation

Upgrade to version 1.0.7

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16479
- https://hackerone.com/reports/411405
- https://github.com/advisories/GHSA-7c9w-qmrq-ff8r
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/486.json
- https://www.npmjs.com/advisories/772
