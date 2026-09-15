# [M] Consul is vulnerable to arbitrary file read when configured with Kubernetes authentication

## Summary
Severity: Medium
Advisory: GHSA-cpfq-66p2-336j
CVE: CVE-2026-2808
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-cpfq-66p2-336j
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=0 <1.18.21
- Go: `github.com/hashicorp/consul` — affected >=1.22.0-rc1 <1.22.5
- Go: `github.com/hashicorp/consul` — affected >=1.19.0 <1.21.11

## Details
HashiCorp Consul and Consul Enterprise 1.18.20 up to 1.21.10 and 1.22.4 are vulnerable to arbitrary file read when configured with Kubernetes authentication. This vulnerability, CVE-2026-2808, is fixed in Consul 1.18.21, 1.21.11 and 1.22.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2808
- https://discuss.hashicorp.com/t/hcsec-2026-02-consul-vulnerable-to-arbitrary-file-reads-through-the-vault-kubernetes-authentication-provider/77232
- https://github.com/hashicorp/consul
- https://pkg.go.dev/vuln/GO-2026-4690
