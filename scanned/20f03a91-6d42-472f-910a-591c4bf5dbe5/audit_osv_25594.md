# [H] Missing password confirmation when creating app passwords

## Summary
Severity: High
Advisory: CVE-2023-39963
Aliases: GHSA-j4qm-5q5x-54m5
CVSS: 8.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L)
Published: 2023-08-10
Source: https://osv.dev/vulnerability/CVE-2023-39963
Type: osv

## Details
Nextcloud Server provides data storage for Nextcloud, an open source cloud platform. Starting in version 20.0.0 and prior to versions 20.0.14.15, 21.0.9.13, 22.2.10.14, 23.0.12.8, 24.0.12.5, 25.0.9, 26.0.4, and 27.0.1, a missing password confirmation allowed an attacker, after successfully stealing a session from a logged in user, to create app passwords for the victim. Nextcloud server versions 25.0.9, 26.0.4, and 27.0.1 and Nextcloud Enterprise Server versions 20.0.14.15, 21.0.9.13, 22.2.10.14, 23.0.12.9, 24.0.12.5, 25.0.9, 26.0.4, and 27.0.1 contain a patch for this issue. No known workarounds are available.

## References
- https://hackerone.com/reports/2067572
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39963.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-j4qm-5q5x-54m5
- https://nvd.nist.gov/vuln/detail/CVE-2023-39963
- https://github.com/nextcloud/server/pull/39416
