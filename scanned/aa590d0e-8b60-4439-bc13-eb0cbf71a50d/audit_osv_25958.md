# [M] Nextcloud Server user_ldap app logs user passwords in the log file on level debug

## Summary
Severity: Medium
Advisory: CVE-2023-48305
Aliases: GHSA-35p6-4992-w5fr
CVSS: 4.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-48305
Type: osv

## Details
Nextcloud Server provides data storage for Nextcloud, an open source cloud platform. Starting in version 25.0.0 and prior to versions 25.0.11, 26.0.6, and 27.1.0 of Nextcloud Server and Nextcloud Enterprise Server, when the log level was set to debug, the user_ldap app logged user passwords in plaintext into the log file. If the log file was then leaked or shared in any way the users' passwords would be leaked. Nextcloud Server and Nextcloud Enterprise Server versions 25.0.11, 26.0.6, and 27.1.0 contain a patch for this issue. As a workaround, change config setting `loglevel` to `1` or higher (should always be higher than 1 in production environments).

## References
- https://hackerone.com/reports/2101165
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48305.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-35p6-4992-w5fr
- https://nvd.nist.gov/vuln/detail/CVE-2023-48305
- https://github.com/nextcloud/server/issues/38461
- https://github.com/nextcloud/server/pull/40013
