# [H] Mullvad VPN for macOS: Local Privilege Escalation via unverified bundle path in installer

## Summary
Severity: High
Advisory: CVE-2026-32323
Aliases: GHSA-c2g6-w5fq-vw3m
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-32323
Type: osv

## Details
Mullvad VPN is a VPN client app for desktop and mobile. When using macOS with versions 2026.1 and below, Mullvad VPN may allow local privilege escalation during installation or upgrade. The installer package executes binaries from /Applications/Mullvad VPN.app without verifying if the bundle is attacker-controlled or that the path is the legitimate Mullvad application. A user in the admin group can pre-place a crafted application bundle at that location and may be able to achieve code execution as root. Since the issue only affected the installer, there is no immediate need for users to update if they are already running an older version. This issue has been fixed in version 2026.2-beta1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32323.json
- https://github.com/mullvad/mullvadvpn-app/security/advisories/GHSA-c2g6-w5fq-vw3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-32323
- https://github.com/mullvad/mullvadvpn-app/commit/032fdcb927c0b6d3e5e1aba4140d33adf22a6bfb
