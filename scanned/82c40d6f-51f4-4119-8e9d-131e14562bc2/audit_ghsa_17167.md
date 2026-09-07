# [M] Incorrect Access Control in NodeBB

## Summary
Severity: Medium
Advisory: GHSA-qc99-r4wh-c8h6
CVE: CVE-2024-29316
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-29
Source: https://github.com/advisories/GHSA-qc99-r4wh-c8h6
Type: github-advisory

## Affected
- npm: `nodebb` — affected >=0 <3.6.7

## Details
In NodeBB prior to 3.6.7 an attacker was able to access the restricted tabs for the Admin group which are only allowed the the administrators.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29316
- https://github.com/NodeBB/NodeBB
- https://medium.com/%40krityamkarma858041/broken-access-control-nodebb-v3-6-7-eebc59c24deb
- https://nodebb.org/bounty
