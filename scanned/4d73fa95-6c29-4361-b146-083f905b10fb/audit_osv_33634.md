# [M] Nextcloud Desktop 3rdparty applications can create share links via socket API

## Summary
Severity: Medium
Advisory: CVE-2025-47792
Aliases: GHSA-qm2f-959g-7p65
CVSS: 5.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:N)
Published: 2025-05-16
Source: https://osv.dev/vulnerability/CVE-2025-47792
Type: osv

## Details
Nextcloud Desktop is the desktop sync client for Nextcloud. In versions of Nextcloud Desktop prior to 3.15, 3rdparty applications already installed on a user machine can create link shares for almost all data via the socket API. These shares can then be easily sent off to an external service. Nextcloud Desktop fixes the issue in version 3.15. No known workarounds are available.

## References
- https://hackerone.com/reports/1995856
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47792.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-qm2f-959g-7p65
- https://nvd.nist.gov/vuln/detail/CVE-2025-47792
- https://github.com/nextcloud/desktop/pull/7517
