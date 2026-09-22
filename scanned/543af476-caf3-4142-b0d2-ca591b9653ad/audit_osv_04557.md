# [M] Discourse: Regular users can route multipart uploads into the admin backup store

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-46413
Aliases: CVE-2026-46413, GHSA-3mvf-q9rg-w6m7
Ecosystem: Bitnami
Published: 2026-07-15
Source: https://osv.dev/vulnerability/BIT-discourse-2026-46413
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.5.0 <2026.5.1

## Details
Discourse is an open-source discussion platform. Prior to 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5, regular users could route direct S3 multipart uploads through ExternalUploadManager into the admin backup store. This issue is fixed in versions 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5.

## References
- https://github.com/discourse/discourse/commit/1f1ded8dd361d81786bff17b35e1138d6ee299c0
- https://github.com/discourse/discourse/commit/7ddde266617b452152c1bf5f903f6c07be38fc40
- https://github.com/discourse/discourse/commit/a53df26dcf7e50ce2b20bfd5454a0c9d44b8fc7d
- https://github.com/discourse/discourse/commit/abaa664c5df84026efb2ca264ba0f5586c3f2b01
- https://github.com/discourse/discourse/releases/tag/v2026.1.5
- https://github.com/discourse/discourse/releases/tag/v2026.4.2
- https://github.com/discourse/discourse/releases/tag/v2026.5.1
- https://github.com/discourse/discourse/releases/tag/v2026.6.0
- https://github.com/discourse/discourse/security/advisories/GHSA-3mvf-q9rg-w6m7
- https://nvd.nist.gov/vuln/detail/CVE-2026-46413
