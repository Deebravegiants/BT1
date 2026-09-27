# [H] SQL Injection in FileContentProvider  (GHSL-2021-1007)

## Summary
Severity: High
Advisory: BIT-nextcloud-2021-43863
Aliases: CVE-2021-43863, GHSA-vjp2-f63v-w479
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2021-43863
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=0 <3.18.1

## Details
The Nextcloud Android app is the Android client for Nextcloud, a self-hosted productivity platform. The Nextcloud Android app uses content providers to manage its data. Prior to version 3.18.1, the providers `FileContentProvider` and `DiskLruImageCacheFileProvider` have security issues (an SQL injection, and an insufficient permission control, respectively) that allow malicious apps in the same device to access Nextcloud's data bypassing the permission control system. Users should upgrade to version 3.18.1 to receive a patch. There are no known workarounds aside from upgrading.

## References
- https://github.com/nextcloud/android/commit/627caba60e69e223b0fc89c4cb18eaa76a95db95
- https://github.com/nextcloud/android/security/advisories/GHSA-vjp2-f63v-w479
- https://hackerone.com/reports/1358597
- https://nvd.nist.gov/vuln/detail/CVE-2021-43863
