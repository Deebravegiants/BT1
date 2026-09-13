# [M] HashiCorp Consul Ingress Gateway Panic Can Shutdown Servers

## Summary
Severity: Medium
Advisory: GHSA-hj93-5fg3-3chr
CVE: CVE-2022-24687
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-25
Source: https://github.com/advisories/GHSA-hj93-5fg3-3chr
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.8.0 <1.9.15
- Go: `github.com/hashicorp/consul` — affected >=1.10.0 <1.10.8
- Go: `github.com/hashicorp/consul` — affected >=1.11.0 <1.11.3

## Details
HashiCorp Consul and Consul Enterprise 1.8.0 through 1.9.14, 1.10.7, and 1.11.2 has Uncontrolled Resource Consumption. Clusters with at least one ingress gateway configured may allow a user with `service:write` permission to register a specifically-defined service that can cause the Consul server to panic and shutdown. Versions 1.9.15, 1.10.8, and 1.11.3 contain patches for the problem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24687
- https://discuss.hashicorp.com
- https://discuss.hashicorp.com/t/hcsec-2022-05-consul-ingress-gateway-panic-can-shutdown-servers
- https://github.com/hashicorp/consul
- https://security.gentoo.org/glsa/202208-09
- https://security.netapp.com/advisory/ntap-20220331-0006
