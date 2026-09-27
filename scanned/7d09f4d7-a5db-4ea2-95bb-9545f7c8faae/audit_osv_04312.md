# [M] L7 intention authorization bypass via custom public listener

## Summary
Severity: Medium
Advisory: BIT-consul-2026-15970
Aliases: CVE-2026-15970
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-consul-2026-15970
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.20.1 <2.0.3

## Details
Consul Community Edition and Consul Enterprise 1.20.1 through 2.0.2 are vulnerable to an L7 intention authorization bypass when a service proxy is configured with a custom public listener. An authenticated mesh workload may reach HTTP paths that are blocked by a path-based deny intention. This vulnerability, CVE-2026-15970, is fixed in Consul 2.0.3 and Consul Enterprise 1.21.17, 1.22.11, and 2.0.3.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-25-multiple-vulnerabilities-impacting-hashicorp-consul/77629
- https://nvd.nist.gov/vuln/detail/CVE-2026-15970
