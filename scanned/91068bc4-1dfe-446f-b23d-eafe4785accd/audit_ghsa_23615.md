# [M] Kibana Sensitive Data Disclosure

## Summary
Severity: Medium
Advisory: GHSA-hp5f-qqrw-c8gj
CVE: CVE-2021-37939
CWE: CWE-319
Ecosystem: npm
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hp5f-qqrw-c8gj
Type: github-advisory

## Affected
- npm: `kibana` — affected >=7.8.0 <7.15.2

## Details
It was discovered that Kibana’s JIRA connector & IBM Resilient connector could be used to return HTTP response data on internal hosts, which may be intentionally hidden from public view. Using this vulnerability, a malicious user with the ability to create connectors, could utilize these connectors to view limited HTTP response data on hosts accessible to the cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37939
- https://discuss.elastic.co/t/kibana-7-15-2-security-update/288923
