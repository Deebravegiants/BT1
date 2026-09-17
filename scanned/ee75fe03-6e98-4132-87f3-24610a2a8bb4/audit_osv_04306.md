# [M] BIT-consul-2020-28053

## Summary
Severity: Medium
Advisory: BIT-consul-2020-28053
Aliases: CVE-2020-28053, GHSA-6m72-467w-94rh, GO-2024-2505
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-consul-2020-28053
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.8.0 <1.8.6

## Details
HashiCorp Consul and Consul Enterprise 1.2.0 up to 1.8.5 allowed operators with operator:read ACL permissions to read the Connect CA private key configuration. Fixed in 1.6.10, 1.7.10, and 1.8.6.

## References
- https://github.com/hashicorp/consul/blob/master/CHANGELOG.md#186-november-19-2020
- https://security.gentoo.org/glsa/202208-09
- https://www.hashicorp.com/blog/category/consul
- https://nvd.nist.gov/vuln/detail/CVE-2020-28053
