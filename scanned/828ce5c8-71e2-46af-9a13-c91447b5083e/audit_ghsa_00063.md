# [M] cofeescript is malware

## Summary
Severity: Medium
Advisory: GHSA-m6wh-m8m8-6xx5
CVE: CVE-2017-16202
CWE: CWE-506
Ecosystem: npm
Published: 2018-08-06
Source: https://github.com/advisories/GHSA-m6wh-m8m8-6xx5
Type: github-advisory

## Affected
- npm: `cofeescript` — affected 1.0.1

## Details
The `cofeescript` package is a piece of malware that steals sensitive data such as a user's private SSH key and bash history, sending them to attacker controlled locations. 

All versions have been unpublished from the npm registry.


## Recommendation

If you have found `cofeescript` installed in your environment, you should:
1. Delete the package
2. Clear your npm cache
3. Ensure it is not present in any other package.json files on your system
4. Regenerate your SSH keys, registry credentials, tokens, and any other sensitive credentials that may have been present in your bash history.

Additionally, any service which may have been exposed via credentials in your bash history or accessible via your ssh keys, such as a database, should be reviewed for indicators of compromise as well.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16202
- https://github.com/advisories/GHSA-m6wh-m8m8-6xx5
- https://www.npmjs.com/advisories/541
