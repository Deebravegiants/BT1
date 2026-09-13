# [H] closurecompiler downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-hjgp-8ffr-hwwr
CVE: CVE-2016-10582
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-hjgp-8ffr-hwwr
Type: github-advisory

## Affected
- npm: `closurecompiler` — affected >=0

## Details
Affected versions of `closurecompiler` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `closurecompiler`.


## Recommendation

Update to version 1.6.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10582
- https://github.com/dcodeIO/ClosureCompiler.js/commit/e59848f5975e5b15279c044daf9cff8ff192bae6
- https://github.com/advisories/GHSA-hjgp-8ffr-hwwr
- https://www.npmjs.com/advisories/169
