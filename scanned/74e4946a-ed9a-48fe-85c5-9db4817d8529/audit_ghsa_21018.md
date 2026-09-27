# [H] OctoPrint Improper Privilege Management vulnerability

## Summary
Severity: High
Advisory: GHSA-2p75-q37p-f852
CVE: CVE-2022-3068
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-2p75-q37p-f852
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.8.3

## Details
OctoPrint prior to 1.8.3 allows a user with read access only to access a privileged user's account and functionality. Version 1.8.3 contains a patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3068
- https://github.com/octoprint/octoprint/commit/ef95ef1c101b79394f134e8fce000e6bae046571
- https://github.com/octoprint/octoprint
- https://github.com/pypa/advisory-database/tree/main/vulns/octoprint/PYSEC-2022-283.yaml
- https://huntr.dev/bounties/f45c24cb-9104-4c6e-a9e1-5c7e75e83884
