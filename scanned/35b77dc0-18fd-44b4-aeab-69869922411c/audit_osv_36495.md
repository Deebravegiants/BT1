# [M] openCryptoki has improper link resolution before file access (link following)

## Summary
Severity: Medium
Advisory: CVE-2026-23893
Aliases: GHSA-j6c7-mvpx-jx5q
CVSS: 6.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:L)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/CVE-2026-23893
Type: osv

## Details
openCryptoki is a PKCS#11 library and provides tooling for Linux and AIX. Versions 2.3.2 and above are vulnerable to symlink-following when running in privileged contexts. A token-group user can redirect file operations to arbitrary filesystem targets by planting symlinks in group-writable token directories, resulting in privilege escalation or data exposure. Token and lock directories are 0770 (group-writable for token users), so any token-group member can plant files and symlinks inside them. When run as root, the base code handling token directory file access, as well as several openCryptoki tools used for administrative purposes, may reset ownership or permissions on existing files inside the token directories. An attacker with token-group membership can exploit the system when an administrator runs a PKCS#11 application or administrative tool that performs chown on files inside the token directory during normal maintenance. This issue is fixed in commit 5e6e4b4, but has not been included in a released version at the time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23893.json
- https://github.com/opencryptoki/opencryptoki/security/advisories/GHSA-j6c7-mvpx-jx5q
- https://nvd.nist.gov/vuln/detail/CVE-2026-23893
- https://github.com/opencryptoki/opencryptoki/commit/5e6e4b42f2b1fcc1e4ef1b920e463bfa55da8b45
