# [M] Hashicorp Consul Improper Neutralization of HTTP Headers for Scripting Syntax vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5c4w-8hhh-3c3h
CVE: CVE-2024-10006
CWE: CWE-116, CWE-644
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-10-31
Source: https://github.com/advisories/GHSA-5c4w-8hhh-3c3h
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.9.0 <1.20.1

## Details
A vulnerability was identified in Consul and Consul Enterprise ("Consul") such that using Headers in L7 traffic intentions could bypass HTTP header based access rules.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10006
- https://github.com/hashicorp/consul/pull/21816
- https://github.com/hashicorp/consul/commit/d9206fc7e284a9244af4d62f8653a63ca30bd00c
- https://discuss.hashicorp.com/t/hcsec-2024-23-consul-l7-intentions-vulnerable-to-headers-bypass
- https://github.com/hashicorp/consul
- https://security.netapp.com/advisory/ntap-20250110-0005
