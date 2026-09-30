# [M] Path Traversal in node-srv

## Summary
Severity: Medium
Advisory: GHSA-52r9-g5g6-2hjp
CVE: CVE-2018-3714
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-52r9-g5g6-2hjp
Type: github-advisory

## Affected
- npm: `node-srv` — affected >=0 <2.1.1

## Details
Versions of `node-srv` before 2.1.1 are vulnerable to path traversal allowing a remote attacker to read files from the server that uses `node-srv`.


## Recommendation

Update to version 2.1.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3714
- https://hackerone.com/reports/309124
- https://github.com/advisories/GHSA-52r9-g5g6-2hjp
- https://www.npmjs.com/advisories/588
