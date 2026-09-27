# [H] pf4j vulnerable to remote code execution via loadpluginPath parameter

## Summary
Severity: High
Advisory: GHSA-rvm8-j2cp-j592
CVE: CVE-2023-40827
CWE: CWE-22, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-29
Source: https://github.com/advisories/GHSA-rvm8-j2cp-j592
Type: github-advisory

## Affected
- Maven: `org.pf4j:pf4j` — affected >=0

## Details
An issue in pf4j pf4j v.3.9.0 and before allows a remote attacker to obtain sensitive information and execute arbitrary code via the loadpluginPath parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40827
- https://github.com/pf4j/pf4j/issues/536
- https://github.com/pf4j/pf4j/pull/537
- https://github.com/pf4j/pf4j/pull/537/commits/ed9392069fe14c6c30d9f876710e5ad40f7ea8c1
- https://github.com/pf4j/pf4j
