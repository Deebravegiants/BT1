# [C] Command Injection in pidusage

## Summary
Severity: Critical
Advisory: GHSA-hfq9-rfpv-j8r8
CVE: CVE-2017-16034
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-hfq9-rfpv-j8r8
Type: github-advisory

## Affected
- npm: `pidusage` — affected >=0 <1.1.5

## Details
Affected versions of `pidusage` pass unsanitized input to `child_process.exec()`, resulting in arbitrary code execution in the `ps` method.
 
This package is vulnerable to this PoC on Darwin, SunOS, FreeBSD, and AIX.

Windows and Linux are not vulnerable. 

## Proof of Concept
```
var pid = require('pidusage');
pid.stat('1 && /usr/local/bin/python');
```


## Recommendation

Update to version 1.1.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16034
- https://www.npmjs.com/advisories/356
