# [M] Discourse: Cross-Site Data Exposure via Backup Restore Metacommand Injection in Multisite Deployments

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-59337
Aliases: CVE-2025-59337, GHSA-7xjr-4f4g-9887
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-discourse-2025-59337
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.5.1

## Details
Discourse is an open-source community discussion platform. In versions 3.5.0 and below, malicious meta-commands could be embedded in a backup dump and executed during restore. In multisite setups, this allowed an admin of one site to access data or credentials from other sites. This issue is fixed in version 3.5.1.

## References
- https://github.com/discourse/discourse/commit/43536b60d012cc8084e7e701d6afab9ba01e28a5
- https://github.com/discourse/discourse/security/advisories/GHSA-7xjr-4f4g-9887
- https://nvd.nist.gov/vuln/detail/CVE-2025-59337
