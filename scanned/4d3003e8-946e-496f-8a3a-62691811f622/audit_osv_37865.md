# [H] Chamilo LMS Affected by Remote Code Execution via eval() in Platform Settings

## Summary
Severity: High
Advisory: CVE-2026-33618
Aliases: GHSA-hp4w-jmwc-pg7w
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-33618
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to .0.0-RC.3, the PlatformConfigurationController::decodeSettingArray() method uses PHP's eval() to parse platform settings from the database. An attacker with admin access (obtainable via Advisory 1) can inject arbitrary PHP code into the settings, which is then executed when any user (including unauthenticated) requests /platform-config/list. This vulnerability is fixed in 2.0.0-RC.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33618.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-hp4w-jmwc-pg7w
- https://nvd.nist.gov/vuln/detail/CVE-2026-33618
- https://github.com/chamilo/chamilo-lms/commit/f2c382c94a3f153a4d7e5ce5686c5a219fd09b3b
