# [H] Downloads Resources over HTTP in mystem3

## Summary
Severity: High
Advisory: GHSA-747p-jfqv-f43r
CVE: CVE-2016-10626
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-747p-jfqv-f43r
Type: github-advisory

## Affected
- npm: `mystem3` — affected >=0 <1.0.8

## Details
Affected versions of `mystem3` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `mystem3`.


## Recommendation

Update to version 1.0.8 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10626
- https://github.com/koorchik/node-mystem3/commit/4bd31c0e0110afc327c414d7ebfc2ffe738cbad2
- https://github.com/advisories/GHSA-747p-jfqv-f43r
- https://www.npmjs.com/advisories/229
