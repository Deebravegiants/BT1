# [M] Salt's on demand pillar functionality vulnerable to arbitrary command injections 

## Summary
Severity: Medium
Advisory: GHSA-fcr4-h6c4-rvvp
CVE: CVE-2025-22237
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-fcr4-h6c4-rvvp
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=3006.0rc1 <3006.12
- PyPI: `salt` — affected >=3007.0rc1 <3007.4

## Details
An attacker with access to a minion key can exploit the 'on demand' pillar functionality with a specially crafted git url which could cause and arbitrary command to be run on the master with the same privileges as the master process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22237
- https://github.com/saltstack/salt/commit/9445f496fed61b15dc4364818007e5b765b0746f
- https://docs.saltproject.io/en/3006/topics/releases/3006.12.html
- https://docs.saltproject.io/en/3007/topics/releases/3007.4.html
- https://github.com/saltstack/salt
