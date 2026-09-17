# [H] Downloads Resources over HTTP in haxe

## Summary
Severity: High
Advisory: GHSA-g785-775g-f2g8
CVE: CVE-2016-10602
CWE: CWE-269, CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-g785-775g-f2g8
Type: github-advisory

## Affected
- npm: `haxe` — affected >=0 <5.0.10

## Details
Affected versions of `haxe` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `haxe`.


## Recommendation

Update to version 5.0.10 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10602
- https://github.com/HaxeFoundation/npm-haxe
- https://www.npmjs.com/advisories/177
