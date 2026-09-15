# [M] FreeScout has Arbitrary File Read in App Logs Viewer via Forged Encrypted Path

## Summary
Severity: Medium
Advisory: CVE-2026-53594
Aliases: GHSA-858x-8f77-9vc5
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-53594
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. FreeScout's `Manage -> Logs -> App Logs` feature uses the bundled `rap2hpoutre/laravel-log-viewer` override to decrypt a user-supplied file identifier and then pass the resolved path to Laravel's download response. Prior to version 1.8.224, the path resolution logic accepts any existing absolute path before applying the intended `storage/logs` restriction. As a result, an attacker who can access the App Logs route and forge a valid Laravel-encrypted `dl` parameter can download arbitrary server-local files readable by the PHP process, not just log files. Version 1.8.224 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53594.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-858x-8f77-9vc5
- https://nvd.nist.gov/vuln/detail/CVE-2026-53594
