# [H] DataEase vulnerable to SQL injection

## Summary
Severity: High
Advisory: GHSA-8rv7-g772-pp3j
CVE: CVE-2023-40771
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-01
Source: https://github.com/advisories/GHSA-8rv7-g772-pp3j
Type: github-advisory

## Affected
- Maven: `io.dataease:dataease-plugin-common` — affected >=0

## Details
SQL injection vulnerability in DataEase v.1.18.9 allows a remote attacker to obtain sensitive information via a crafted string outside of the blacklist function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40771
- https://github.com/dataease/dataease/issues/5861
- https://github.com/dataease/dataease
