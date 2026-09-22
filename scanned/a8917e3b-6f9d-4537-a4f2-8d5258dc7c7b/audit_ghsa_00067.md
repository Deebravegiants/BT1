# [M] jquey is malware

## Summary
Severity: Medium
Advisory: GHSA-6fjr-m7v6-fpg9
CVE: CVE-2017-16204
CWE: CWE-506
Ecosystem: npm
Published: 2018-08-06
Source: https://github.com/advisories/GHSA-6fjr-m7v6-fpg9
Type: github-advisory

## Affected
- npm: `jquey` — affected 1.0.1

## Details
The `jquey` package is malware that attempts to discover and exfiltrate sensitive data such as a user's private SSH key and bash history, sending them to attacker controlled locations. 

All versions have been unpublished from the npm registry.


## Recommendation

If you have found `jquey` installed in your environment, you should:
1. Delete the package
2. Clear your npm cache
3. Ensure it is not present in any other package.json files on your system
4. Regenerate your SSH keys, registry credentials, tokens, and any other sensitive credentials that may have been present in your bash history.

Additionally, any service which may have been exposed via credentials in your bash history or accessible via your ssh keys, such as a database, should be reviewed for indicators of compromise as well.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16204
- https://github.com/advisories/GHSA-6fjr-m7v6-fpg9
- https://www.npmjs.com/advisories/544
