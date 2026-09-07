# [H] Missing Authorization in HashiCorp Consul

## Summary
Severity: High
Advisory: GHSA-gw2g-hhc9-wgjh
CVE: CVE-2022-3920
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-gw2g-hhc9-wgjh
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.13.0 <1.14.0

## Details
HashiCorp Consul and Consul Enterprise 1.13.0 up to 1.13.3 do not filter cluster filtering's imported nodes and services for HTTP or RPC endpoints used by the UI. Fixed in 1.14.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3920
- https://github.com/hashicorp/consul/commit/706866fa0016b0aa302679f9c648859050d19b2e
- https://discuss.hashicorp.com/t/hcsec-2022-28-consul-cluster-peering-leaks-imported-nodes-services-information/46946
