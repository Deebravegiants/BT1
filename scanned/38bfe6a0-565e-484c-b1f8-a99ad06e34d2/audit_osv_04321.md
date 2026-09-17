# [M] Unauthenticated denial of service via unbounded request body processing

## Summary
Severity: Medium
Advisory: BIT-consul-2026-19113
Aliases: CVE-2026-19113
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-consul-2026-19113
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.3.0 <2.0.3

## Details
Consul Community Edition and Consul Enterprise 1.3.0 through 2.0.2 are vulnerable to an unauthenticated denial of service in several agent HTTP API endpoints. A remote caller could cause the agent to consume substantial memory before the request was rejected. This vulnerability, CVE-2026-19113, is fixed in Consul 2.0.3 and Consul Enterprise 1.21.17, 1.22.11, and 2.0.3.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-25-multiple-vulnerabilities-impacting-hashicorp-consul/77629
- https://nvd.nist.gov/vuln/detail/CVE-2026-19113
