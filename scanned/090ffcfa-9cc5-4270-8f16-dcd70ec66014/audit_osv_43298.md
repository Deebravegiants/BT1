# [H] Electerm check folder size function may get attacked by unsafe folder name

## Summary
Severity: High
Advisory: CVE-2026-73224
Aliases: GHSA-4wx8-4m69-8rw5
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73224
Type: osv

## Details
electerm is an open-sourced terminal/ssh/sftp/telnet/serialport/RDP/VNC/Spice/ftp client. Prior to 3.15.120, electerm allows a malicious FTP or SFTP server to execute arbitrary commands when a user downloads a crafted folder and invokes Properties and Calculate Size because calcLocal in src/client/components/sftp/file-info-modal.jsx inserts the server-controlled folder name into a du -sh shell command without safely escaping single quotes. This issue is fixed in version 3.15.120.

## References
- https://github.com/electerm/electerm/releases/tag/v3.15.120
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73224.json
- https://github.com/electerm/electerm/security/advisories/GHSA-4wx8-4m69-8rw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-73224
- https://github.com/electerm/electerm/commit/36b16fb66936bb7c65fbcdf706dfd1b77f0750a7
