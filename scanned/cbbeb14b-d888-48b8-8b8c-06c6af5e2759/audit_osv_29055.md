# [M] aimeos/ai-admin-jsonadm improper access control vulnerability allows editors to remove required records

## Summary
Severity: Medium
Advisory: CVE-2024-39322
Aliases: GHSA-8fj2-587w-5whr
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-07-02
Source: https://osv.dev/vulnerability/CVE-2024-39322
Type: osv

## Details
aimeos/ai-admin-jsonadm is the Aimeos e-commerce JSON API for administrative tasks. In versions prior to 2020.10.13, 2021.10.6, 2022.10.3, 2023.10.4, and 2024.4.2, improper access control allows editors to remove admin group and locale configuration in the Aimeos backend. Versions 2020.10.13, 2021.10.6, 2022.10.3, 2023.10.4, and 2024.4.2 contain a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39322.json
- https://github.com/aimeos/ai-admin-jsonadm/security/advisories/GHSA-8fj2-587w-5whr
- https://nvd.nist.gov/vuln/detail/CVE-2024-39322
- https://github.com/aimeos/ai-admin-jsonadm/commit/02a063fbd616d4e0a5aaf89f1642a856aa5ac5a5
- https://github.com/aimeos/ai-admin-jsonadm/commit/16d013d0e28cecd19781f434d83fabebcc78cdc2
- https://github.com/aimeos/ai-admin-jsonadm/commit/4c966e02bd52589c3c9382777cfe170eddf17b00
- https://github.com/aimeos/ai-admin-jsonadm/commit/640954243ce85c2c303a00dd6481ed39b3d218fb
- https://github.com/aimeos/ai-admin-jsonadm/commit/7d1c05e8368b0a6419820fe402deac9960500026
