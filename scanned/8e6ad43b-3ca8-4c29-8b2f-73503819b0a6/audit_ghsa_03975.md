# [H] Downloads Resources over HTTP in embedza

## Summary
Severity: High
Advisory: GHSA-mq7g-6rv4-pj95
CVE: CVE-2016-10569
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-mq7g-6rv4-pj95
Type: github-advisory

## Affected
- npm: `embedza` — affected >=0 <1.2.4

## Details
Affected versions of `embedza` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `embedza`.


## Recommendation

Update to version 1.2.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10569
- https://github.com/advisories/GHSA-mq7g-6rv4-pj95
- https://www.npmjs.com/advisories/187
