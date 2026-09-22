# [C] ZimaOS has Authentication Bypass via System-Level Username

## Summary
Severity: Critical
Advisory: CVE-2026-21891
Aliases: GHSA-xj93-qw9p-jxq4
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2026-21891
Type: osv

## Details
ZimaOS is a fork of CasaOS, an operating system for Zima devices and x86-64 systems with UEFI. In versions up to and including 1.5.0, the application checks the validity of the username but appears to skip, misinterpret, or incorrectly validate the password when the provided username matches a known system service account. The application's login function fails to properly handle the password validation result for these users, effectively granting authenticated access to anyone who knows one of these common usernames and provides any password. As of time of publication, no known patched versions are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21891.json
- https://github.com/IceWhaleTech/ZimaOS/security/advisories/GHSA-xj93-qw9p-jxq4
- https://nvd.nist.gov/vuln/detail/CVE-2026-21891
