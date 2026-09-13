# [H] Downloads Resources over HTTP in selenium-download

## Summary
Severity: High
Advisory: GHSA-2mvm-66q7-m256
CVE: CVE-2016-10559
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-2mvm-66q7-m256
Type: github-advisory

## Affected
- npm: `selenium-download` — affected >=0 <2.0.7

## Details
Affected versions of `selenium-download` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `selenium-download`.


## Recommendation

Update to version 2.0.7 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10559
- https://github.com/advisories/GHSA-2mvm-66q7-m256
- https://www.npmjs.com/advisories/164
