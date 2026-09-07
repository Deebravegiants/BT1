# [H] install-nw downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-wq7q-7vfh-2x3h
CVE: CVE-2016-10566
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-wq7q-7vfh-2x3h
Type: github-advisory

## Affected
- npm: `install-nw` — affected >=0 <1.1.5

## Details
Affected versions of `install-nw` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `install-nw`.


## Recommendation

Update to version 1.1.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10566
- https://github.com/advisories/GHSA-wq7q-7vfh-2x3h
- https://www.npmjs.com/advisories/204
