# [M] Discourse allows script execution in uploaded HTML/XML files on S3

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-66488
Aliases: CVE-2025-66488, GHSA-68jp-3934-62rx
Ecosystem: Bitnami
Published: 2026-02-02
Source: https://osv.dev/vulnerability/BIT-discourse-2025-66488
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.0

## Details
Discourse is an open source discussion platform. A vulnerability present in versions prior to 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0 affects anyone who uses S3 for uploads. While scripts may be executed, they will only be run in the context of the S3/CDN domain, with no site credentials. Versions 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0 fix the issue. As a workaround, disallow html or xml files for uploads in authorized_extensions. For existing html xml uploads, site owners can consider deleting them.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-68jp-3934-62rx
- https://nvd.nist.gov/vuln/detail/CVE-2025-66488
