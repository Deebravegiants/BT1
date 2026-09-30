# [H] LAM has Authenticated Local File Inclusion (LFI) in PDF export

## Summary
Severity: High
Advisory: CVE-2026-27894
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-27894
Type: osv

## Details
LDAP Account Manager (LAM) is a webfrontend for managing entries (e.g. users, groups, DHCP settings) stored in an LDAP directory. Prior to version 9.5, a local file inclusion was detected in the PDF export that allows users to include local PHP files and this way execute code. In combination with GHSA-88hf-2cjm-m9g8 this allows to execute arbitrary code. Users need to login to LAM to exploit this vulnerability. Version 9.5 fixes the issue. Although upgrading is recommended, a workaround would be to make /var/lib/ldap-account-manager/config read-only for the web-server user and delete the PDF profile files (making PDF exports impossible).

## References
- https://github.com/LDAPAccountManager/lam/releases/tag/9.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27894.json
- https://github.com/LDAPAccountManager/lam/security/advisories/GHSA-88hf-2cjm-m9g8
- https://github.com/LDAPAccountManager/lam/security/advisories/GHSA-w7xq-vjr3-p9cf
- https://nvd.nist.gov/vuln/detail/CVE-2026-27894
