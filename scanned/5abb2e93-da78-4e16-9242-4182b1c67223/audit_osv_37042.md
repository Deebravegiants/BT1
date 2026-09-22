# [M] LAM has incorrect regular expression in PDF export component that allows user to upload files of any type

## Summary
Severity: Medium
Advisory: CVE-2026-27895
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-27895
Type: osv

## Details
LDAP Account Manager (LAM) is a webfrontend for managing entries (e.g. users, groups, DHCP settings) stored in an LDAP directory. Prior to version 9.5, the PDF export component does not correctly validate uploaded file extensions. This way any file type (including .php files) can be uploaded. With GHSA-w7xq-vjr3-p9cf, an attacker can achieve remote code execution as the web server user. Version 9.5 fixes the issue. Although upgrading is recommended, a workaround would be to make /var/lib/ldap-account-manager/config read-only for the web-server user.

## References
- https://github.com/LDAPAccountManager/lam/releases/tag/9.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27895.json
- https://github.com/LDAPAccountManager/lam/security/advisories/GHSA-88hf-2cjm-m9g8
- https://github.com/LDAPAccountManager/lam/security/advisories/GHSA-w7xq-vjr3-p9cf
- https://nvd.nist.gov/vuln/detail/CVE-2026-27895
