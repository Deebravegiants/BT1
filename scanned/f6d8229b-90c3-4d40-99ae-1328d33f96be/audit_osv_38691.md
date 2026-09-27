# [C] Krayin CRM 2.2.4 Missing Authentication via install/api/admin-config-setup

## Summary
Severity: Critical
Advisory: CVE-2026-41452
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-41452
Type: osv

## Details
Krayin CRM 2.2.4 contains a missing authentication vulnerability in the installer middleware that allows unauthenticated remote attackers to overwrite the primary administrator account by sending a crafted HTTP POST request with the X-Requested-With: XMLHttpRequest header to bypass the CanInstall middleware redirect check. Attackers can supply arbitrary name, email, and password values to the admin-config-setup endpoint, which performs an unauthenticated updateOrInsert targeting the hardcoded administrator user ID, enabling full administrative access to all CRM data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41452.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41452
- https://www.vulncheck.com/advisories/krayin-crm-missing-authentication-via-install-api-admin-config-setup
- https://github.com/krayin/laravel-crm
- https://jivasecurity.com/writeups/krayin-installer-bypass-account-takeover-cve-2026-41452
