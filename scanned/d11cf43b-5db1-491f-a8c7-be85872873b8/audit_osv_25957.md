# [M] Nextcloud Server vulnerable to attacker enabling/disabling birthday calendar for any user

## Summary
Severity: Medium
Advisory: CVE-2023-48304
Aliases: GHSA-8jwv-c8c8-9fr3
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-48304
Type: osv

## Details
Nextcloud Server provides data storage for Nextcloud, an open source cloud platform. Starting in version 25.0.0 and prior to versions 25.0.11, 26.0.6, and 27.1.0 of Nextcloud Server and starting in version 22.0.0 and prior to versions 22.2.10.16, 23.0.12.11, 24.0.12.7, 25.0.11, 26.0.6, and 27.1.0 of Nextcloud Enterprise Server, an attacker could enable and disable the birthday calendar for any user on the same server. Nextcloud Server 25.0.11, 26.0.6, and 27.1.0 and Nextcloud Enterprise Server 22.2.10.16, 23.0.12.11, 24.0.12.7, 25.0.11, 26.0.6, and 27.1.0 contain patches for this issue. No known workarounds are available.

## References
- https://hackerone.com/reports/2112973
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48304.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-8jwv-c8c8-9fr3
- https://nvd.nist.gov/vuln/detail/CVE-2023-48304
- https://github.com/nextcloud/server/pull/40292
