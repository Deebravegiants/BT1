# [M] Consul Server Panic when Ingress and API Gateways Configured with Peering Connections

## Summary
Severity: Medium
Advisory: GHSA-wj6x-hcc2-f32j
CVE: CVE-2023-0845
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-09
Source: https://github.com/advisories/GHSA-wj6x-hcc2-f32j
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.14.0 <1.14.5

## Details
A vulnerability was identified in Consul and Consul Enterprise (“Consul”) an authenticated user with service:write permissions could trigger a workflow that causes Consul server and client agents to crash under certain circumstances. To exploit this vulnerability, an attacker requires access to an ACL token with service:write permissions, and there needs to be at least one running ingress or API gateway that is configured to route traffic to an upstream service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0845
- https://discuss.hashicorp.com/t/hcsec-2023-06-consul-server-panic-when-ingress-and-api-gateways-configured-with-peering-connections/51197
- https://github.com/hashicorp/consul
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LYZOKMMVX4SIEHPJW3SJUQGMO5YZCPHC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XNF4OLYZRQE75EB5TW5N42FSXHBXGWFE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZTE4ITXXPIWZEQ4HYQCB6N6GZIMWXDAI
