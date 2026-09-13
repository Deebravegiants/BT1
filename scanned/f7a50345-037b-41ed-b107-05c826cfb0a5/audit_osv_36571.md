# [M] Icinga has insecure permission of %ProgramData%\icinga2\var on Windows

## Summary
Severity: Medium
Advisory: CVE-2026-24413
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2026-24413
Type: osv

## Details
Icinga 2 is an open source monitoring system. Starting in version 2.3.0 and prior to versions 2.13.14, 2.14.8, and 2.15.2, the Icinga 2 MSI did not set appropriate permissions for the `%ProgramData%\icinga2\var` folder on Windows. This resulted in the its contents - including the private key of the user and synced configuration - being readable by all local users. All installations on Windows are affected. Versions 2.13.14, 2.14.8, and 2.15.2 contains a fix. There are two possibilities to work around the issue without upgrading Icinga 2. Upgrade Icinga for Windows to at least version v1.13.4, v1.12.4, or v1.11.2. These version will automatically fix the ACLs for the Icinga 2 agent as well. Alternatively, manually update the ACL for the given folder `C:\ProgramData\icinga2\var` (and `C:\Program Files\WindowsPowerShell\modules\icinga-powershell-framework\certificate` to fix the issue for the Icinga for Windows as well) including every sub-folder and item to restrict access for general users, only allowing the Icinga service user and administrators access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24413.json
- https://github.com/Icinga/icinga-powershell-framework/security/advisories/GHSA-88h5-rrm6-5973
- https://github.com/Icinga/icinga2/security/advisories/GHSA-vfjg-6fpv-4mmr
- https://nvd.nist.gov/vuln/detail/CVE-2026-24413
- https://icinga.com/blog/releasing-icinga-2-v2-15-2-v2-14-8-v2-13-14-and-icinga-for-windows-v1-13-4-v1-12-4-v1-11-2
