# [M] Cross-site Scripting in bootstrap-table

## Summary
Severity: Medium
Advisory: GHSA-grw5-g9h2-wpg8
CVE: CVE-2022-1726
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-grw5-g9h2-wpg8
Type: github-advisory

## Affected
- npm: `bootstrap-table` — affected >=0 <1.20.2

## Details
Bootstrap Tables XSS vulnerability with Table Export plug-in when exportOptions: htmlContent is true in GitHub repository wenzhixin/bootstrap-table prior to 1.20.2. Disclosing session cookies, disclosing secure session data, exfiltrating data to third-parties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1726
- https://github.com/wenzhixin/bootstrap-table/commit/b4a1e5dd332be652e0bc376fd9256886cf4bbde9
- https://github.com/wenzhixin/bootstrap-table
- https://huntr.dev/bounties/9b85cc33-0395-4c31-8a42-3a94beb2efea
