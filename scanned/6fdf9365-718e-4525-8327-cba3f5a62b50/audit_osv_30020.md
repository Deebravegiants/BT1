# [H] ZimaOS (Installed Applications and System Information) has Unauthorized Sensitive Data Leak

## Summary
Severity: High
Advisory: CVE-2024-49357
Aliases: GHSA-hg2h-q5h6-r5c4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-24
Source: https://osv.dev/vulnerability/CVE-2024-49357
Type: osv

## Details
ZimaOS is a fork of CasaOS, an operating system for Zima devices and x86-64 systems with UEFI. In version 1.2.4 and all prior versions, the API endpoints in ZimaOS, such as `http://<Server-IP>/v1/users/image?path=/var/lib/casaos/1/app_order.json` and `http://<Server-IP>/v1/users/image?path=/var/lib/casaos/1/system.json`, expose sensitive data like installed applications and system information without requiring any authentication or authorization. This sensitive data leak can be exploited by attackers to gain detailed knowledge about the system setup, installed applications, and other critical information. As of time of publication, no known patched versions are available.

## References
- https://youtu.be/H_WoqzM-9Cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49357.json
- https://github.com/IceWhaleTech/ZimaOS/security/advisories/GHSA-hg2h-q5h6-r5c4
- https://nvd.nist.gov/vuln/detail/CVE-2024-49357
