# [M] Authenticated denial of service in Consul Enterprise-to-Community Edition downgrade path

## Summary
Severity: Medium
Advisory: BIT-consul-2026-19012
Aliases: CVE-2026-19012
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-consul-2026-19012
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.18.0 <2.0.3

## Details
Consul Community Edition and Consul Enterprise 1.18.0 through 2.0.2 are vulnerable to an authenticated denial of service in the Enterprise-to-Community Edition downgrade path that may allow an authorized caller to crash the Consul server. A caller with config-entry write permission can submit a service-router configuration entry that causes the agent to exit unexpectedly. This vulnerability, CVE-2026-19012, is fixed in Consul 2.0.3 and Consul Enterprise 1.21.17, 1.22.11, and 2.0.3.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-25-multiple-vulnerabilities-impacting-hashicorp-consul/77629
- https://nvd.nist.gov/vuln/detail/CVE-2026-19012
