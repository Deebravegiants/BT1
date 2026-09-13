# [H] Command Injection in tree-kill

## Summary
Severity: High
Advisory: GHSA-884p-74jh-xrg2
CVE: CVE-2019-15599
CWE: CWE-94
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-884p-74jh-xrg2
Type: github-advisory

## Affected
- npm: `tree-kill` — affected >=0 <1.2.2

## Details
Versions of `tree-kill` prior to 1.2.2 are vulnerable to Command Injection. The package fails to sanitize values passed to the  `kill` function. If this value is user-controlled it  may allow attackers to run arbitrary commands in the server. The issue only affects Windows systems.


## Recommendation

Upgrade to version 1.2.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15599
- https://github.com/pkrumins/node-tree-kill/commit/deee138a8cbc918463d8af5ce8c2bec33c3fd164
- https://hackerone.com/reports/701183
- https://github.com/pkrumins/node-tree-kill
- https://github.com/pkrumins/node-tree-kill/releases/tag/v1.2.2
