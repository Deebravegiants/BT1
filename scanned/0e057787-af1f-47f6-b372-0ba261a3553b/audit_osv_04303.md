# [H] BIT-consul-2020-13250

## Summary
Severity: High
Advisory: BIT-consul-2020-13250
Aliases: CVE-2020-13250, GHSA-rqjq-mrgx-85hp, GO-2022-0879
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-consul-2020-13250
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.7.0 <1.7.4

## Details
HashiCorp Consul and Consul Enterprise include an HTTP API (introduced in 1.2.0) and DNS (introduced in 1.4.3) caching feature that was vulnerable to denial of service. Fixed in 1.6.6 and 1.7.4.

## References
- https://github.com/hashicorp/consul/blob/v1.6.6/CHANGELOG.md
- https://github.com/hashicorp/consul/blob/v1.7.4/CHANGELOG.md
- https://github.com/hashicorp/consul/pull/8023
- https://nvd.nist.gov/vuln/detail/CVE-2020-13250
