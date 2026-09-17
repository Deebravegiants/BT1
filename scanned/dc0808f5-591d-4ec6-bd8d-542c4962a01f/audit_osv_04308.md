# [H] BIT-consul-2021-41805

## Summary
Severity: High
Advisory: BIT-consul-2021-41805
Aliases: CVE-2021-41805
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-consul-2021-41805
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.10.0 <1.10.4

## Details
HashiCorp Consul Enterprise before 1.8.17, 1.9.x before 1.9.11, and 1.10.x before 1.10.4 has Incorrect Access Control. An ACL token (with the default operator:write permissions) in one namespace can be used for unintended privilege escalation in a different namespace.

## References
- https://discuss.hashicorp.com/t/hcsec-2021-29-consul-enterprise-namespace-default-acls-allow-privilege-escalation/31871
- https://security.netapp.com/advisory/ntap-20211229-0007/
- https://www.hashicorp.com/blog/category/consul
- https://nvd.nist.gov/vuln/detail/CVE-2021-41805
