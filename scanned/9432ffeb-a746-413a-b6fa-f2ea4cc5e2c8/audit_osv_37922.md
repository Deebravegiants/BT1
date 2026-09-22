# [C] MyTube has an Unauthenticated Admin Privilege Escalation via Passkey Registration

## Summary
Severity: Critical
Advisory: CVE-2026-33890
Aliases: GHSA-378w-xh68-qrc8
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33890
Type: osv

## Details
MyTube is a self-hosted downloader and player for several video websites Prior to version 1.8.71, an unauthenticated attacker can register an arbitrary passkey and subsequently authenticate with it to obtain a full admin session. The application exposes passkey registration endpoints without requiring prior authentication. Any successfully authenticated passkey is automatically granted an administrator token, allowing full administrative access to the application. This enables a complete compromise of the application without requiring any existing credentials. Version 1.8.71 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33890.json
- https://github.com/franklioxygen/MyTube/security/advisories/GHSA-378w-xh68-qrc8
- https://nvd.nist.gov/vuln/detail/CVE-2026-33890
- https://github.com/franklioxygen/MyTube/commit/d6c1275a7ff7ffd3d51b53c333237f4d572580ac
