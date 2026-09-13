# [M] Nextcloud: Lack of authenticity of metadata keys allows a malicious server to gain access to E2EE folders

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2023-28999
Aliases: CVE-2023-28999, GHSA-8875-wxww-3rr8
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2023-28999
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=3.0.5 <4.8.0

## Details
Nextcloud is an open-source productivity platform. In Nextcloud Desktop client 3.0.0 until 3.8.0, Nextcloud Android app 3.13.0 until 3.25.0, and Nextcloud iOS app 3.0.5 until 4.8.0, a malicious server administrator can gain full access to an end-to-end encrypted folder. They can decrypt files, recover the folder structure and add new files.​ This issue is fixed in Nextcloud Desktop 3.8.0, Nextcloud Android 3.25.0, and Nextcloud iOS 4.8.0. No known workarounds are available.

## References
- https://ethz.ch/content/dam/ethz/special-interest/infk/inst-infsec/appliedcrypto/education/theses/report_DanieleCoppola.pdf
- https://github.com/nextcloud/desktop/pull/5560
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-8875-wxww-3rr8
- https://nvd.nist.gov/vuln/detail/CVE-2023-28999
