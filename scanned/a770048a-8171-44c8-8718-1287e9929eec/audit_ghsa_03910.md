# [H] ibm_db downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-c4qp-h3m6-785f
CVE: CVE-2016-10577
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-c4qp-h3m6-785f
Type: github-advisory

## Affected
- npm: `ibm_db` — affected >=0 <1.0.2

## Details
Affected versions of `ibm_db` insecurely download resources over HTTP. 

In scenarios where an attacker has a privileged network position, they can modify or read such resources at will. While the exact severity of impact for a vulnerability like this is highly variable and depends on the behavior of the package itself, it ranges from being able to read sensitive information all the way up to and including remote code execution.


## Recommendation

Update to version 1.0.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10577
- https://github.com/ibmdb/node-ibm_db/commit/d7e2d4b4cbeb6f067df8bba7d0b2ac5d40fcfc19#diff-315091eb1586966006e05ebc21cd2a94
- https://github.com/advisories/GHSA-c4qp-h3m6-785f
- https://www.npmjs.com/advisories/163
