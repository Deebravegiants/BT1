# [M] Missing brute force protection on password reset token OAuth2 API controller

## Summary
Severity: Medium
Advisory: CVE-2023-39958
Aliases: GHSA-vv27-g2hq-v48h
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2023-08-10
Source: https://osv.dev/vulnerability/CVE-2023-39958
Type: osv

## Details
Nextcloud Server provides data storage for Nextcloud, an open source cloud platform. Starting in version 22.0.0 and prior to versions 22.2.10.13, 23.0.12.8, 24.0.12.5, 25.0.9, 26.0.4, and 27.0.1, missing protection allows an attacker to brute force the client secrets of configured OAuth2 clients. Nextcloud Server versions 25.0.9, 26.0.4, and 27.0.1 and Nextcloud Enterprise Server versions 22.2.10.13, 23.0.12.8, 24.0.12.5, 25.0.9, 26.0.4, and 27.0.1 contain a patch for this issue. No known workarounds are available.

## References
- https://hackerone.com/reports/1258448
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39958.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-vv27-g2hq-v48h
- https://nvd.nist.gov/vuln/detail/CVE-2023-39958
- https://github.com/nextcloud/server/pull/38773
