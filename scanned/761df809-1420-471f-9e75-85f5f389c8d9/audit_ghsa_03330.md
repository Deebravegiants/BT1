# [M] Improper Input Validation in HashiCorp Consul

## Summary
Severity: Medium
Advisory: GHSA-p2j5-3f4c-224r
CVE: CVE-2020-13170
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-p2j5-3f4c-224r
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.6.0-beta1 <1.6.6
- Go: `github.com/hashicorp/consul` — affected >=1.7.0 <1.7.4

## Details
HashiCorp Consul and Consul Enterprise did not appropriately enforce scope for local tokens issued by a primary data center, where replication to a secondary data center was not enabled. Introduced in 1.4.0, fixed in 1.6.6 and 1.7.4.
### Specific Go Packages Affected
github.com/hashicorp/consul/agent

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13170
- https://github.com/hashicorp/consul/pull/8068
- https://github.com/hashicorp/consul/commit/242994a016a181d6c62a5bb83189716ad13d4216
- https://github.com/hashicorp/consul/blob/v1.6.6/CHANGELOG.md
- https://github.com/hashicorp/consul/blob/v1.7.4/CHANGELOG.md
