# [M] Consul vulnerable to partial arbitrary file read via Vault Connect CA provider

## Summary
Severity: Medium
Advisory: BIT-consul-2026-19017
Aliases: CVE-2026-19017
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-consul-2026-19017
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.18.21 <2.0.3

## Details
Consul Community Edition and Consul Enterprise 1.18.21 through 2.0.2 are vulnerable to a partial arbitrary file read when configured to use the Vault Connect CA provider with JWT or AppRole authentication. A privileged attacker with `operator:write` permission may direct Consul to read and forward credential files outside the intended scope, potentially leading to the exfiltration of sensitive secrets from the Consul server host. This vulnerability, CVE-2026-19017, is fixed in Consul 2.0.3 and Consul Enterprise 1.21.17, 1.22.11, and 2.0.3.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-25-multiple-vulnerabilities-impacting-hashicorp-consul/77629
- https://nvd.nist.gov/vuln/detail/CVE-2026-19017
