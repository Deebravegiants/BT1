# [H] Unauthenticated denial of service via unbounded external gRPC connection acceptance

## Summary
Severity: High
Advisory: BIT-consul-2026-15972
Aliases: CVE-2026-15972
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-consul-2026-15972
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.13.0 <2.0.3

## Details
Consul Community Edition and Consul Enterprise 1.13.0 through 2.0.2 are vulnerable to an unauthenticated denial of service through unbounded connection acceptance on the external gRPC listeners. A remote attacker may exhaust agent file descriptors, goroutines, and memory by opening many incomplete connections, potentially preventing legitimate clients from connecting. This vulnerability, CVE-2026-15972, is fixed in Consul 2.0.3 and Consul Enterprise 1.21.17, 1.22.11, and 2.0.3.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-25-multiple-vulnerabilities-impacting-hashicorp-consul/77629
- https://nvd.nist.gov/vuln/detail/CVE-2026-15972
