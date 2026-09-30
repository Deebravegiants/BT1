# [H] HashiCorp Consul vulnerable to Origin Validation Error

## Summary
Severity: High
Advisory: GHSA-q7fx-wm2p-qfj8
CVE: CVE-2019-9764
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-q7fx-wm2p-qfj8
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=0 <1.4.4

## Details
HashiCorp Consul 1.4.3 lacks server hostname verification for agent-to-agent TLS communication. In other words, the product behaves as if `verify_server_hostname` were set to false, even when it is actually set to true. This is fixed in 1.4.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9764
- https://github.com/hashicorp/consul/issues/5519
- https://github.com/hashicorp/consul/commit/7e11dd82aa8dae505b7307adcb68c9d3194b3b40
- https://github.com/hashicorp/consul
