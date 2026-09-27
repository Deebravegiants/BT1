# [M] Incorrect Authorization in HashiCorp Consul

## Summary
Severity: Medium
Advisory: GHSA-r9w6-rhh9-7v53
CVE: CVE-2020-7955
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-07-28
Source: https://github.com/advisories/GHSA-r9w6-rhh9-7v53
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.4.1 <1.6.3

## Details
HashiCorp Consul and Consul Enterprise 1.4.1 through 1.6.2 did not uniformly enforce ACLs across all API endpoints, resulting in potential unintended information disclosure. Fixed in 1.6.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7955
- https://github.com/hashicorp/consul/issues/7160
- https://www.hashicorp.com/blog/category/consul
