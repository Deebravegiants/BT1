# [C] Code injection in kill-process-by-name

## Summary
Severity: Critical
Advisory: GHSA-qc65-cgvr-93p6
CVE: CVE-2021-23356
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-19
Source: https://github.com/advisories/GHSA-qc65-cgvr-93p6
Type: github-advisory

## Affected
- npm: `kill-process-by-name` — affected >=0

## Details
This affects all versions of package kill-process-by-name. If (attacker-controlled) user input is given, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization in the index.js file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23356
- https://snyk.io/vuln/SNYK-JS-KILLPROCESSBYNAME-1078534
