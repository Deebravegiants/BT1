# [H] ZimaOS: Unauthorized Creation of Files/Folders in Restricted System Directories via API

## Summary
Severity: High
Advisory: CVE-2026-28286
Aliases: GHSA-65mg-9gw5-vr7g
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2026-28286
Type: osv

## Details
ZimaOS is a fork of CasaOS, an operating system for Zima devices and x86-64 systems with UEFI. In version 1.5.2-beta3, the application enforces restrictions in the frontend/UI to prevent users from creating files or folders in internal OS paths. However, when interacting directly with the API, the restrictions are bypass-able. By sending a crafted request targeting paths like /etc, /usr, or other sensitive system directories, the API successfully creates files or directories in locations where normal users should have no write access. This indicates that the API does not properly validate the target path, allowing unauthorized operations on critical system directories. No known patch is publicly available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28286.json
- https://github.com/IceWhaleTech/ZimaOS/security/advisories/GHSA-65mg-9gw5-vr7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-28286
