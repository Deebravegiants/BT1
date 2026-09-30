# [C] Atheos Improper Input Validation Vulnerability Enables RCE in Common.php

## Summary
Severity: Critical
Advisory: CVE-2025-49008
Aliases: GHSA-rwc2-4q8c-xj48
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-06-05
Source: https://osv.dev/vulnerability/CVE-2025-49008
Type: osv

## Details
Atheos is a self-hosted browser-based cloud integrated development environment. Prior to version 6.0.4, improper use of `escapeshellcmd()` in `/components/codegit/traits/execute.php` allows argument injection, leading to arbitrary command execution. Atheos administrators and users of vulnerable versions are at risk of data breaches or server compromise. Version 6.0.4 introduces a `Common::safe_execute` function that sanitizes all arguments using `escapeshellarg()` prior to execution and migrated all components potentially vulnerable to similar exploits to use this new templated execution system.

## References
- https://github.com/Atheos/Atheos/security/advisories/GHSA-rwc2-4q8c-xj48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49008.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-49008
- https://github.com/Atheos/Atheos/commit/7e6c0eb45fa6d04d786a0037389540f2638fe792
