# [M] Vault Enterprise Leaks Sensitive HTTP Request Headers in the Audit Log When Deployed With a Performance Standby Node

## Summary
Severity: Medium
Advisory: BIT-vault-2024-2877
Aliases: CVE-2024-2877
Ecosystem: Bitnami
Published: 2024-05-02
Source: https://osv.dev/vulnerability/BIT-vault-2024-2877
Type: osv

## Affected
- Bitnami: `vault` — affected >=1.15.0 <1.15.8

## Details
Vault Enterprise, when configured with performance standby nodes and a configured audit device, will inadvertently log request headers on the standby node. These logs may have included sensitive HTTP request information in cleartext.

This vulnerability, CVE-2024-2877, was fixed in Vault Enterprise 1.15.8.

## References
- https://discuss.hashicorp.com/t/hsec-2024-10-vault-enterprise-leaks-sensitive-http-request-headers-in-audit-log-when-deployed-with-a-performance-standby-node
- https://nvd.nist.gov/vuln/detail/CVE-2024-2877
- https://security.netapp.com/advisory/ntap-20240614-0002/
