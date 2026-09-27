# [M] Path Traversal in takeapeek

## Summary
Severity: Medium
Advisory: GHSA-23xp-j737-282v
CVE: CVE-2018-16473
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-11-06
Source: https://github.com/advisories/GHSA-23xp-j737-282v
Type: github-advisory

## Affected
- npm: `takeapeek` — affected >=0

## Details
All versions of `takeapeek` are vulnerable to path traversal exposing files and directories.


## Recommendation

As no fix is currently available for this vulnerability is it is our recommendation to use another static file server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16473
- https://hackerone.com/reports/403736
- https://github.com/advisories/GHSA-23xp-j737-282v
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/478.json
- https://www.npmjs.com/advisories/740
