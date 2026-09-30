# [H] BIT-consul-2021-28156

## Summary
Severity: High
Advisory: BIT-consul-2021-28156
Aliases: CVE-2021-28156
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-consul-2021-28156
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.9.0 <1.9.5

## Details
HashiCorp Consul Enterprise version 1.8.0 up to 1.9.4 audit log can be bypassed by specifically crafted HTTP events. Fixed in 1.9.5, and 1.8.10.

## References
- https://discuss.hashicorp.com/t/hcsec-2021-08-consul-enterprise-audit-log-bypass-for-http-events/23369
- https://security.gentoo.org/glsa/202208-09
- https://www.hashicorp.com/blog/category/consul
- https://nvd.nist.gov/vuln/detail/CVE-2021-28156
