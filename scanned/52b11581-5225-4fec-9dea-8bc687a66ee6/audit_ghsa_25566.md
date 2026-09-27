# [C] Use of Externally-Controlled Format String in consoleme

## Summary
Severity: Critical
Advisory: GHSA-74w3-2r77-fw5h
CVE: CVE-2022-27177
CWE: CWE-134
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-03
Source: https://github.com/advisories/GHSA-74w3-2r77-fw5h
Type: github-advisory

## Affected
- PyPI: `consoleme` — affected >=0 <1.2.2

## Details
A Python format string issue leading to information disclosure and potentially remote code execution in ConsoleMe for all versions prior to 1.2.2

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27177
- https://github.com/Netflix/consoleme/commit/2a3c84eee524d77c427b3329a8419cbbce9e1d16
- https://github.com/Netflix/ConsoleMe
- https://github.com/Netflix/security-bulletins/blob/master/advisories/nflx-2022-001.md
- https://github.com/pypa/advisory-database/tree/main/vulns/consoleme/PYSEC-2022-189.yaml
