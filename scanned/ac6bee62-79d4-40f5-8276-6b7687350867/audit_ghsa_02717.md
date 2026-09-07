# [H] HashiCorp Consul Privilege Escalation Vulnerability

## Summary
Severity: High
Advisory: GHSA-ccw8-7688-vqx4
CVE: CVE-2021-37219
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-08
Source: https://github.com/advisories/GHSA-ccw8-7688-vqx4
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.10.1 <1.10.2
- Go: `github.com/hashicorp/consul` — affected >=1.9.0 <1.9.9
- Go: `github.com/hashicorp/consul` — affected >=0 <1.8.15

## Details
HashiCorp Consul and Consul Enterprise 1.10.1 Raft RPC layer allows non-server agents with a valid certificate signed by the same CA to access server-only functionality, enabling privilege escalation. Fixed in 1.8.15, 1.9.9 and 1.10.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37219
- https://github.com/hashicorp/consul/pull/10925
- https://github.com/hashicorp/consul/commit/3357e57dac9aadabd476f7a14973e47f003c4cf0
- https://github.com/hashicorp/consul/commit/473edd1764b6739e2e4610ea5dede4c2bc6009d1
- https://github.com/hashicorp/consul/commit/ccf8eb1947357434eb6e66303ddab79f4c9d4103
- https://discuss.hashicorp.com/t/hcsec-2021-22-consul-raft-rpc-privilege-escalation/29024
- https://github.com/hashicorp/consul
- https://security.gentoo.org/glsa/202207-01
- https://www.hashicorp.com/blog/category/consul
