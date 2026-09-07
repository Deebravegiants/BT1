# [H] Prototype Pollution in merge

## Summary
Severity: High
Advisory: GHSA-f9cm-qmx5-m98h
CVE: CVE-2018-16469
CWE: CWE-1321, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-11-01
Source: https://github.com/advisories/GHSA-f9cm-qmx5-m98h
Type: github-advisory

## Affected
- npm: `merge` — affected >=0 <1.2.1

## Details
Versions of `merge` before 1.2.1 are vulnerable to prototype pollution. The `merge.recursive` function can be tricked into adding or modifying properties of the Object prototype.


## Recommendation

Update to version 1.2.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16469
- https://hackerone.com/reports/381194
- https://github.com/advisories/GHSA-f9cm-qmx5-m98h
- https://www.npmjs.com/advisories/722
