# [H] electerm: Path traversal in editWithSystemEditor temp file path via unsanitized SFTP filename

## Summary
Severity: High
Advisory: CVE-2026-73223
Aliases: GHSA-4cgc-4vgf-q55c
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73223
Type: osv

## Details
electerm is an open-sourced terminal/ssh/sftp/telnet/serialport/RDP/VNC/Spice/ftp client. Prior to 3.15.120, electerm allows a malicious SFTP server to write attacker-controlled content outside the temporary directory because the server-controlled filename name used by editWithSystemEditor in src/client/components/sftp/file-item.jsx is interpolated into path.resolve without sanitization. This issue is fixed in version 3.15.120.

## References
- https://github.com/electerm/electerm/releases/tag/v3.15.120
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73223.json
- https://github.com/electerm/electerm/security/advisories/GHSA-4cgc-4vgf-q55c
- https://nvd.nist.gov/vuln/detail/CVE-2026-73223
- https://github.com/electerm/electerm/commit/32ea29365762b3451b1f2fcc0ef78104384db282
