# [M] Vault Vulnerable to Privilege Escalation via Slash Injection in Templated Policy Paths

## Summary
Severity: Medium
Advisory: BIT-vault-2026-5006
Aliases: CVE-2026-5006
Ecosystem: Bitnami
Published: 2026-08-28
Source: https://osv.dev/vulnerability/BIT-vault-2026-5006
Type: osv

## Affected
- Bitnami: `vault` — affected >=0.11.0 <2.0.4

## Details
A vulnerability was identified in HashiCorp Vault and Vault Enterprise (“Vault”) such that an authenticated attacker may manipulate an identity value referenced by a templated policy path to gain unintended access to Vault paths.

An attacker who can control the referenced identity value may include slash ({{/}}) characters that Vault interprets as additional path segments when rendering the policy.

This vulnerability, CVE-2026-5006, was fixed in Vault Community Edition 2.0.4 and Vault Enterprise 2.0.4, 1.21.9, 1.20.14, and 1.19.20.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-32-vault-vulnerable-to-privilege-escalation-via-slash-injection-in-templated-policy-paths
- https://nvd.nist.gov/vuln/detail/CVE-2026-5006
