# [H] Antilles Dependency Confusion Vulnerability

## Summary
Severity: High
Advisory: GHSA-hgc3-hp6x-wpgx
CVE: CVE-2021-3840
CWE: CWE-427
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-03
Source: https://github.com/advisories/GHSA-hgc3-hp6x-wpgx
Type: github-advisory

## Affected
- PyPI: `antilles-tools` — affected >=0 <1.0.1

## Details
### Potential Impact: 
Remote code execution.

### Scope of Impact: 
Open-source project specific.

### Summary Description:
A dependency confusion vulnerability was reported in the Antilles open-source software prior to version 1.0.1 that could allow for remote code execution during installation due to a package listed in requirements.txt not existing in the public package index (PyPi). 
MITRE classifies this weakness as an Uncontrolled Search Path Element (CWE-427) in which a private package dependency may be replaced by an unauthorized package of the same name published to a well-known public repository such as PyPi.
The configuration has been updated to only install components built by Antilles, removing all other public package indexes. Additionally, the antilles-tools dependency has been published to PyPi.

### Mitigation Strategy for Customers (what you should do to protect yourself):
Remove previous versions of Antilles as a precautionary measure and Update to version 1.0.1 or later.

### Acknowledgement:
The Antilles team thanks Kotko Vladyslav for reporting this issue.

### References:
https://github.com/lenovo/Antilles/commit/c7b9c5740908b343aceefe69733d9972e64df0b9

## References
- https://github.com/lenovo/Antilles/security/advisories/GHSA-hgc3-hp6x-wpgx
- https://nvd.nist.gov/vuln/detail/CVE-2021-3840
- https://github.com/lenovo/Antilles/commit/c7b9c5740908b343aceefe69733d9972e64df0b9
- https://github.com/lenovo/Antilles
- https://github.com/pypa/advisory-database/tree/main/vulns/antilles-tools/PYSEC-2021-840.yaml
