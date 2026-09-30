# [M] Craft CMS has a theoretical bypass for CVE-2025-23209

## Summary
Severity: Medium
Advisory: GHSA-2vcf-qxv3-2mgw
CVE: CVE-2025-54417
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-2vcf-qxv3-2mgw
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.13.8 <4.16.3
- Packagist: `craftcms/cms` — affected >=5.5.8 <5.8.4

## Details
**Pre-requisites:**

* Have a compromised security key (https://craftcms.com/knowledge-base/securing-craft#keep-your-secrets-secret)
* Somehow, manage to create an arbitrary file in Craft’s `/storage/backups` folder.

With those two pieces in place, you could create a specific, malicious request to the `/updater/restore-db` endpoint to execute CLI commands remotely.

Fixed in https://github.com/craftcms/cms/commit/a19d46be78a9ca1ea474012a10e97bed0d787f57

-----

Reported by Marco O. (segfault)

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-2vcf-qxv3-2mgw
- https://nvd.nist.gov/vuln/detail/CVE-2025-23209
- https://nvd.nist.gov/vuln/detail/CVE-2025-54417
- https://github.com/craftcms/cms/commit/a19d46be78a9ca1ea474012a10e97bed0d787f57
- https://github.com/craftcms/cms
