# [M] CVE-2025-3908

## Summary
Severity: Medium
Advisory: CVE-2025-3908
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-05-19
Source: https://osv.dev/vulnerability/CVE-2025-3908
Type: osv

## Details
The configuration initialization tool in OpenVPN 3 Linux v20 through v24 on Linux allows a local attacker to use symlinks pointing at an arbitrary directory which will change the ownership and permissions of that destination directory.

## References
- https://community.openvpn.net/Security%20Announcements/CVE-2025-3908
- http://www.openwall.com/lists/oss-security/2025/05/20/2
