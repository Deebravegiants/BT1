# [M] Hijacked Environment Variables in proxy.js

## Summary
Severity: Medium
Advisory: GHSA-qj73-v688-wqxf
CVE: CVE-2017-16076
CWE: CWE-506
Ecosystem: npm
Published: 2018-08-29
Source: https://github.com/advisories/GHSA-qj73-v688-wqxf
Type: github-advisory

## Affected
- npm: `proxy.js` — affected >=0

## Details
The `proxy.js` package is a piece of malware that steals environment variables and sends them to attacker controlled locations. 

All versions have been unpublished from the npm registry.


## Recommendation


As this package is malware, if you find it installed in your environment, the real security concern is determining how it got there. 

If you have found this installed in your environment, you should:
1. Delete the package
2. Clear your npm cache
3. Ensure it is not present in any other package.json files on your system
4. Regenerate your registry credentials, tokens, and any other sensitive credentials that may have been present in your environment variables. 

Additionally, any service which may have been exposed via credentials in your environment variables, such as a database, should be reviewed for indicators of compromise as well.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16076
- https://github.com/advisories/GHSA-qj73-v688-wqxf
- https://www.npmjs.com/advisories/515
