# [C] Vault Secrets Operator vulnerable to arbitrary file read and credential exfiltration via AppRole secretIDPath

## Summary
Severity: Critical
Advisory: BIT-consul-2026-8715
Aliases: CVE-2026-8715
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-consul-2026-8715
Type: osv

## Affected
- Bitnami: `consul` — affected >=1.3.0 <1.5.0

## Details
Vault Secrets Operator 1.3.0 up to 1.4.1 is vulnerable to an arbitrary file read and credential exfiltration issue in the AppRole authentication configuration that may allow a tenant with limited Kubernetes RBAC permissions to read files from the operator pod's filesystem and transmit their contents to a tenant-controlled endpoint, potentially leading to privilege escalation within the cluster. This vulnerability (CVE-2026-8715) is fixed in Vault Secrets Operator 1.5.0.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-28-vault-secrets-operator-vulnerable-to-arbitrary-file-read-via-approle-secretidpath/77645
- https://nvd.nist.gov/vuln/detail/CVE-2026-8715
- http://www.openwall.com/lists/oss-security/2026/08/28/3
