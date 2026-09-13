# [M] Database resource exhaustion for logged-in users via sharee recommendations with circles

## Summary
Severity: Medium
Advisory: CVE-2022-39330
Aliases: GHSA-wxx7-w5p4-7x4c
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-10-27
Source: https://osv.dev/vulnerability/CVE-2022-39330
Type: osv

## Details
Nextcloud Server is the file server software for Nextcloud, a self-hosted productivity platform. Nextcloud Server prior to versions 23.0.10 and 24.0.6 and Nextcloud Enterprise Server prior to versions 22.2.10, 23.0.10, and 24.0.6 are vulnerable to a logged-in attacker slowing down the system by generating a lot of database/cpu load. Nextcloud Server versions 23.0.10 and 24.0.6 and Nextcloud Enterprise Server versions 22.2.10, 23.0.10, and 24.0.6 contain patches for this issue. As a workaround, disable the Circles app.

## References
- https://hackerone.com/reports/1688199
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39330.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-wxx7-w5p4-7x4c
- https://nvd.nist.gov/vuln/detail/CVE-2022-39330
- https://github.com/nextcloud/circles/pull/1147
