# [H] pf4j vulnerable to remote code execution via expandIfZip method in the extract function

## Summary
Severity: High
Advisory: GHSA-cj8w-v588-p8wx
CVE: CVE-2023-40828
CWE: CWE-22, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-29
Source: https://github.com/advisories/GHSA-cj8w-v588-p8wx
Type: github-advisory

## Affected
- Maven: `org.pf4j:pf4j` — affected >=0

## Details
An issue in pf4j pf4j v.3.9.0 and before allows a remote attacker to obtain sensitive information and execute arbitrary code via the expandIfZip method in the extract function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40828
- https://github.com/pf4j/pf4j/pull/537
- https://github.com/pf4j/pf4j/pull/538
- https://github.com/pf4j/pf4j/commit/8e0aa198c4e652cfc1eb9e05ca9b64397f67cc72
- https://github.com/pf4j/pf4j
