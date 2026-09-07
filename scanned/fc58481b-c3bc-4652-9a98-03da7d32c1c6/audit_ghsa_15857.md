# [H] Hashicorp Consul Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-chgm-7r52-whjj
CVE: CVE-2024-10005
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-10-31
Source: https://github.com/advisories/GHSA-chgm-7r52-whjj
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.9.0 <1.20.1

## Details
A vulnerability was identified in Consul and Consul Enterprise ("Consul") such that using URL paths in L7 traffic intentions could bypass HTTP request path-based access rules.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10005
- https://github.com/hashicorp/consul/pull/21816
- https://github.com/hashicorp/consul/commit/d9206fc7e284a9244af4d62f8653a63ca30bd00c
- https://discuss.hashicorp.com/t/hcsec-2024-22-consul-l7-intentions-vulnerable-to-url-path-bypass
- https://github.com/advisories/GHSA-chgm-7r52-whjj
- https://github.com/hashicorp/consul
- https://security.netapp.com/advisory/ntap-20250110-0004
