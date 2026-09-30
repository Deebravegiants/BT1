# [M] Uncontrolled resource consumption in the Consul Connect authorization endpoint

## Summary
Severity: Medium
Advisory: BIT-consul-2026-19014
Aliases: CVE-2026-19014
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-consul-2026-19014
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.17.0 <2.0.3

## Details
Consul Community Edition and Consul Enterprise 1.17.0 through 2.0.2 are vulnerable to an uncontrolled resource consumption issue in the Connect authorization endpoint that may allow a caller to grow the agent's intention-match cache without bound, defeating the operator's cache-disable configuration. This vulnerability, CVE-2026-190124, is fixed in Consul 2.0.3 and Consul Enterprise 1.21.17, 1.22.11, and 2.0.3.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-25-multiple-vulnerabilities-impacting-hashicorp-consul/77629
- https://nvd.nist.gov/vuln/detail/CVE-2026-19014
