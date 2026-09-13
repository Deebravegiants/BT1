# [M] NitroShare Desktop 0.3.4 Path Traversal via LAN File Transfer Server

## Summary
Severity: Medium
Advisory: CVE-2026-66050
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-66050
Type: osv

## Details
NitroShare Desktop through 0.3.4 contains a path traversal vulnerability in its LAN file transfer server that allows unauthenticated attackers on the same network to write arbitrary files by sending a crafted filename containing directory traversal sequences in the JSON item header name field. Attackers can exploit the lack of path validation to write files outside the transfer root directory to arbitrary locations the current user has write access, including the Windows Startup folder, enabling persistent code execution on the next user login.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66050.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66050
- https://www.vulncheck.com/advisories/nitroshare-desktop-path-traversal-via-lan-file-transfer-server
- https://github.com/nitroshare/nitroshare-desktop
- https://github.com/cduram/NotCVE-2026-0009
