# [H] Consul Cluster Peering can Result in Denial of Service

## Summary
Severity: High
Advisory: BIT-consul-2023-1297
Aliases: CVE-2023-1297, GHSA-c57c-7hrj-6q6v, GO-2023-1827
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-consul-2023-1297
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.15.0 <1.15.3

## Details
Consul and Consul Enterprise's cluster peering implementation contained a flaw whereby a peer cluster with service of the same name as a local service could corrupt Consul state, resulting in denial of service. This vulnerability was resolved in Consul 1.14.5, and 1.15.3

## References
- https://discuss.hashicorp.com/t/hcsec-2023-15-consul-cluster-peering-can-result-in-denial-of-service/54515
- https://nvd.nist.gov/vuln/detail/CVE-2023-1297
