# [H] ZimaOS: Arbitrary Deletion of Internal System Files via API Path Manipulation

## Summary
Severity: High
Advisory: CVE-2026-28442
Aliases: GHSA-q5hp-59wm-9xq3
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-28442
Type: osv

## Details
ZimaOS is a fork of CasaOS, an operating system for Zima devices and x86-64 systems with UEFI. In version 1.5.2-beta3, users are restricted from deleting internal system files or folders through the application interface. However, when interacting directly with the API, these restrictions can be bypassed. By altering the path parameter in the delete request, internal OS files and directories can be removed successfully. The backend processes these manipulated requests without validating whether the targeted path belongs to restricted system locations. This demonstrates improper input validation and broken access control on sensitive filesystem operations. No known public patch is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28442.json
- https://github.com/IceWhaleTech/ZimaOS/security/advisories/GHSA-q5hp-59wm-9xq3
- https://nvd.nist.gov/vuln/detail/CVE-2026-28442
