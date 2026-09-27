# [H] BIT-consul-2020-25201

## Summary
Severity: High
Advisory: BIT-consul-2020-25201
Aliases: CVE-2020-25201, GHSA-496g-fr33-whrf, GO-2024-2501
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-consul-2020-25201
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.7.0

## Details
HashiCorp Consul Enterprise version 1.7.0 up to 1.8.4 includes a namespace replication bug which can be triggered to cause denial of service via infinite Raft writes. Fixed in 1.7.9 and 1.8.5.

## References
- https://github.com/hashicorp/consul/blob/master/CHANGELOG.md#185-october-23-2020
- https://security.gentoo.org/glsa/202208-09
- https://www.hashicorp.com/blog/category/consul
