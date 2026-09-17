# [H] Denial of Service (DoS) in HashiCorp Consul

## Summary
Severity: High
Advisory: GHSA-23jv-v6qj-3fhh
CVE: CVE-2020-7219
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-23jv-v6qj-3fhh
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=0 <1.6.3

## Details
HashiCorp Consul and Consul Enterprise up to 1.6.2 HTTP/RPC services allowed unbounded resource usage, and were susceptible to unauthenticated denial of service. Fixed in 1.6.3.

### Specific Go Packages Affected
github.com/hashicorp/consul/agent/consul

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7219
- https://github.com/hashicorp/consul/issues/7159
- https://www.hashicorp.com/blog/category/consul
