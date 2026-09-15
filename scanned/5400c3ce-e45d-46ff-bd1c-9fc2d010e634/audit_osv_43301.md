# [H] electerm's RDP clipboard file download may parse unsafe file name

## Summary
Severity: High
Advisory: CVE-2026-73227
Aliases: GHSA-gm6q-5vpx-3mwf
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73227
Type: osv

## Details
electerm is an open-sourced terminal/ssh/sftp/telnet/serialport/RDP/VNC/Spice/ftp client. Prior to 3.15.120, electerm allows a malicious RDP server to write attacker-controlled content outside the selected save directory because the RDP clipboard download path in src/client/components/rdp/file-transfer.js passes the server-controlled CLIPRDR filename fileInfo.name to osResolve without sanitization. This issue is fixed in version 3.15.120.

## References
- https://github.com/electerm/electerm/releases/tag/v3.15.120
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73227.json
- https://github.com/electerm/electerm/security/advisories/GHSA-gm6q-5vpx-3mwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-73227
- https://github.com/electerm/electerm/commit/451bf3000672c00b0c3b148fbf3c148c205ce350
