# [M] Icinga for Windows certificate can have too-open permissions

## Summary
Severity: Medium
Advisory: CVE-2026-24414
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2026-24414
Type: osv

## Details
The Icinga PowerShell Framework provides configuration and check possibilities to ensure integration and monitoring of Windows environments. In versions prior to 1.13.4, 1.12.4, and 1.11.2, permissions of the Icinga for Windows `certificate` directory grant every user read access, which results in the exposure of private key of the Icinga certificate for the given host. All installations are affected. Versions 1.13.4, 1.12.4, and 1.11.2 contains a patch. Please note that upgrading to a fixed version of Icinga for Windows will also automatically fix a similar issue present in Icinga 2, CVE-2026-24413. As a workaround, the permissions can be restricted manually by updating the ACL for the given folder `C:\Program Files\WindowsPowerShell\modules\icinga-powershell-framework\certificate` (and `C:\ProgramData\icinga2\var` to fix the issue for the Icinga 2 agent as well) including every sub-folder and item to restrict access for general users, only allowing the Icinga service user and administrators access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24414.json
- https://github.com/Icinga/icinga-powershell-framework/security/advisories/GHSA-88h5-rrm6-5973
- https://github.com/Icinga/icinga2/security/advisories/GHSA-vfjg-6fpv-4mmr
- https://nvd.nist.gov/vuln/detail/CVE-2026-24414
- https://icinga.com/blog/releasing-icinga-2-v2-15-2-v2-14-8-v2-13-14-and-icinga-for-windows-v1-13-4-v1-12-4-v1-11-2
