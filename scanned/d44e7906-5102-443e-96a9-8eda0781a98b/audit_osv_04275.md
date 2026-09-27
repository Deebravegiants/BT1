# [H] Bridgecrew Checkov: Unsafe deserialization of Terraform files allows code execution

## Summary
Severity: High
Advisory: BIT-checkov-2021-3035
Aliases: CVE-2021-3035
Ecosystem: Bitnami
Published: 2026-02-09
Source: https://osv.dev/vulnerability/BIT-checkov-2021-3035
Type: osv

## Affected
- Bitnami: `checkov` — affected >=2.0.0 <2.0.26

## Details
An unsafe deserialization vulnerability in Bridgecrew Checkov by Prisma Cloud allows arbitrary code execution when processing a malicious terraform file. This issue impacts Checkov 2.0 versions earlier than Checkov 2.0.26. Checkov 1.0 versions are not impacted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3035
- https://security.paloaltonetworks.com/CVE-2021-3035
