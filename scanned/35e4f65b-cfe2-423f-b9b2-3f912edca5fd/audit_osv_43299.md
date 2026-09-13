# [H] electerm: Path traversal in FTP/SFTP recursive folder download via unsanitized server filename

## Summary
Severity: High
Advisory: CVE-2026-73225
Aliases: GHSA-6wh4-q387-x93j
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73225
Type: osv

## Details
electerm is an open-sourced terminal/ssh/sftp/telnet/serialport/RDP/VNC/Spice/ftp client. Prior to 3.15.120, electerm allows a malicious FTP or SFTP server to write attacker-controlled content outside the selected download directory because recursive transfers in src/client/components/file-transfer/transfer.jsx pass server-supplied file.name and folder.name values to resolve without sanitization. This issue is fixed in version 3.15.120.

## References
- https://github.com/electerm/electerm/releases/tag/v3.15.120
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73225.json
- https://github.com/electerm/electerm/security/advisories/GHSA-6wh4-q387-x93j
- https://nvd.nist.gov/vuln/detail/CVE-2026-73225
- https://github.com/electerm/electerm/commit/deee11ffe558eaee5cad5822949ba3a7f87ae56a
