# [H] Command Injection in psnode

## Summary
Severity: High
Advisory: GHSA-m8fm-mv5w-33pv
CVE: CVE-2021-23375
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-m8fm-mv5w-33pv
Type: github-advisory

## Affected
- npm: `psnode` — affected >=0

## Details
This affects all current versions of package psnode. If attacker-controlled user input is given to the kill function, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23375
- https://github.com/nrako/psnode
- https://github.com/nrako/psnode/blob/076f623689e4506d3647505daca13b3f482e0c31/lib/index.js#23L59
- https://snyk.io/vuln/SNYK-JS-PSNODE-1078543
- https://www.npmjs.com/package/psnode
