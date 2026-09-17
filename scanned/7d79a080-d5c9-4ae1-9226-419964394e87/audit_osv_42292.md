# [C] phpMyFAQ before 4.1.6 Remote Code Execution via Configuration API

## Summary
Severity: Critical
Advisory: CVE-2026-66398
Aliases: GHSA-4fv7-8rr6-rf2w
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-66398
Type: osv

## Details
phpMyFAQ before v4.1.6 contains a remote code execution vulnerability in the configuration API that allows authenticated administrators with CONFIGURATION_EDIT and ATTACHMENT_ADD privileges to write arbitrary PHP files by manipulating the upgrade.lastDownloadedPackage setting. Attackers can upload a malicious ZIP file as an attachment, point the updater configuration to its stored path, and extract it into the application root to achieve code execution as the web server user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66398.json
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-4fv7-8rr6-rf2w
- https://nvd.nist.gov/vuln/detail/CVE-2026-66398
- https://www.vulncheck.com/advisories/phpmyfaq-before-remote-code-execution-via-configuration-api
