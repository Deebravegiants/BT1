# [M] Tunnelblick arbitrary file read via symlink following in tunnelblickd

## Summary
Severity: Medium
Advisory: CVE-2026-31893
Aliases: GHSA-927j-vcjf-hq69
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-31893
Type: osv

## Details
Tunnelblick is an open source graphic user interface for OpenVPN on macOS. In versions 3.3beta26 through 9.0beta01, any local user can read arbitrary root-owned files by exploiting a symlink following vulnerability in tunnelblick-helper, reachable through the world-accessible tunnelblickd Unix socket. The socket is configured with mode 0666, allowing any local user to connect. No authorization check is performed on the connecting client. The tunnelblick-helper process constructs a path to config.ovpn inside a user-controlled .tblk directory and reads it as root without symlink validation. An attacker can create a .tblk configuration with a symlinked config.ovpn pointing to any file and request tunnelblickd to read it. This issue has been fixed in versions 9.0beta02.

## References
- https://github.com/Tunnelblick/Tunnelblick/releases/tag/v9.0beta02
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31893.json
- https://github.com/Tunnelblick/Tunnelblick/security/advisories/GHSA-927j-vcjf-hq69
- https://nvd.nist.gov/vuln/detail/CVE-2026-31893
