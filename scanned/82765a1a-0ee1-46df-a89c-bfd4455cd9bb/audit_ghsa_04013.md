# [H] Downloads Resources over HTTP in aerospike

## Summary
Severity: High
Advisory: GHSA-v5v3-8jqf-vg27
CVE: CVE-2016-10558
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-v5v3-8jqf-vg27
Type: github-advisory

## Affected
- npm: `aerospike` — affected >=0 <2.4.2

## Details
Affected versions of `aerospike` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `aerospike`.


## Recommendation

Update to version 2.4.2 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10558
- https://github.com/advisories/GHSA-v5v3-8jqf-vg27
- https://www.npmjs.com/advisories/167
