# [H] Downloads Resources over HTTP in galenframework-cli

## Summary
Severity: High
Advisory: GHSA-x5ph-4fr4-g7fw
CVE: CVE-2016-10560
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-x5ph-4fr4-g7fw
Type: github-advisory

## Affected
- npm: `galenframework-cli` — affected >=0 <2.3.1

## Details
Affected versions of `galenframework-cli` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `galenframework-cli`.


## Recommendation

Update to version 2.3.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10560
- https://github.com/advisories/GHSA-x5ph-4fr4-g7fw
- https://www.npmjs.com/advisories/170
