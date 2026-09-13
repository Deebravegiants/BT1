# [M] BIT-consul-2020-12797

## Summary
Severity: Medium
Advisory: BIT-consul-2020-12797
Aliases: CVE-2020-12797, GHSA-hwqm-x785-qh8p, GO-2022-0847
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-consul-2020-12797
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.7.0 <1.7.4

## Details
HashiCorp Consul and Consul Enterprise failed to enforce changes to legacy ACL token rules due to non-propagation to secondary data centers. Introduced in 1.4.0, fixed in 1.6.6 and 1.7.4.

## References
- https://github.com/hashicorp/consul/blob/v1.6.6/CHANGELOG.md
- https://github.com/hashicorp/consul/blob/v1.7.4/CHANGELOG.md
- https://github.com/hashicorp/consul/pull/8047
- https://nvd.nist.gov/vuln/detail/CVE-2020-12797
