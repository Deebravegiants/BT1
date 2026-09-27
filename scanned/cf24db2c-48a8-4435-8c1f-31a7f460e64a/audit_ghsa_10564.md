# [H] HashiCorp Vault has a KVv2 Metadata and Secret Deletion Policy Bypass that leads to Denial-of-Service

## Summary
Severity: High
Advisory: GHSA-m2w4-8ggf-rj47
CVE: CVE-2026-3605
CWE: CWE-288
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-m2w4-8ggf-rj47
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0.10.0

## Details
An authenticated user with access to a kvv2 path through a policy containing a glob may be able to delete secrets they were not authorized to read or write, resulting in denial-of-service. This vulnerability did not allow a malicious user to delete secrets across namespaces, nor read any secret data. Fixed in Vault Community Edition 2.0.0 and Vault Enterprise 2.0.0, 1.21.5, 1.20.10, and 1.19.16.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3605
- https://discuss.hashicorp.com/t/hcsec-2026-05-vault-kvv2-metadata-and-secret-deletion-policy-bypass-denial-of-service/77342
- https://github.com/hashicorp/vault
