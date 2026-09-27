# [H] Downloads Resources over HTTP in nodewebkit

## Summary
Severity: High
Advisory: GHSA-gc6c-5v9w-xmhw
CVE: CVE-2016-10580
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-gc6c-5v9w-xmhw
Type: github-advisory

## Affected
- npm: `nodewebkit` — affected >=0

## Details
Affected versions of `nodewebkit` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `nodewebkit`.


## Recommendation

No patch is currently available, and the package author has deprecated this package. 

The best path forward in mitigating this vulnerability is to use the [official installer](https://www.npmjs.com/nw) instead of this package, as per the package author's instructions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10580
- https://github.com/advisories/GHSA-gc6c-5v9w-xmhw
- https://www.npmjs.com/advisories/173
