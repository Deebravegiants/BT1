# [H] BIT-consul-2020-12758

## Summary
Severity: High
Advisory: BIT-consul-2020-12758
Aliases: CVE-2020-12758, GHSA-q2qr-3c2p-9235, GO-2022-0861
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-consul-2020-12758
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.7.0 <1.7.4

## Details
HashiCorp Consul and Consul Enterprise could crash when configured with an abnormally-formed service-router entry. Introduced in 1.6.0, fixed in 1.6.6 and 1.7.4.

## References
- https://github.com/hashicorp/consul/blob/v1.6.6/CHANGELOG.md
- https://github.com/hashicorp/consul/blob/v1.7.4/CHANGELOG.md
- https://github.com/hashicorp/consul/pull/7783
- https://nvd.nist.gov/vuln/detail/CVE-2020-12758
