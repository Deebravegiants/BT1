# [M] Nextcloud Server DNS pin middleware can be tricked into DNS rebinding allowing SSRF

## Summary
Severity: Medium
Advisory: CVE-2023-48306
Aliases: GHSA-8f69-f9jg-4x3v
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-48306
Type: osv

## Details
Nextcloud Server provides data storage for Nextcloud, an open source cloud platform. Starting in version 25.0.0 and prior to versions 25.0.11, 26.0.6, and 27.1.0 of Nextcloud Server and starting in version 22.0.0 and prior to versions 22.2.10.16, 23.0.12.11, 24.0.12.7, 25.0.11, 26.0.6, and 27.1.0 of Nextcloud Enterprise Server, the DNS pin middleware was vulnerable to DNS rebinding allowing an attacker to perform SSRF as a final result. Nextcloud Server 25.0.11, 26.0.6, and 27.1.0 and Nextcloud Enterprise Server 22.2.10.16, 23.0.12.11, 24.0.12.7, 25.0.11, 26.0.6, and 27.1.0 contain patches for this issue. No known workarounds are available.

## References
- https://hackerone.com/reports/2115212
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48306.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-8f69-f9jg-4x3v
- https://nvd.nist.gov/vuln/detail/CVE-2023-48306
- https://github.com/nextcloud/server/pull/40234
