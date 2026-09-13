# [M] Authorization bypass for session deletion in the transaction API

## Summary
Severity: Medium
Advisory: BIT-consul-2026-19016
Aliases: CVE-2026-19016
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-consul-2026-19016
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.19.1 <2.0.3

## Details
Consul Community Edition and Consul Enterprise 1.19.1 through 2.0.2 did not enforce the {{session:write}} ACL permission for session deletion operations submitted through the transaction API. An authenticated caller with network access to the Consul server RPC port could delete arbitrary sessions without holding the required permission. This vulnerability, CVE-2026-19016, is fixed in Consul 2.0.3 and Consul Enterprise 1.21.17, 1.22.11, and 2.0.3.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-25-multiple-vulnerabilities-impacting-hashicorp-consul/77629
- https://nvd.nist.gov/vuln/detail/CVE-2026-19016
