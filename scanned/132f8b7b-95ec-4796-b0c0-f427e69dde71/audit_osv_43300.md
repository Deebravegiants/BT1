# [H] Electerm WebSocket `upgrade-func` and `fs` handlers allow arbitrary method/function invocation due to missing method-name allowlist

## Summary
Severity: High
Advisory: CVE-2026-73226
Aliases: GHSA-8chw-jwc5-8587
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73226
Type: osv

## Details
electerm is an open-sourced terminal/ssh/sftp/telnet/serialport/RDP/VNC/Spice/ftp client. Prior to 3.15.186, electerm allows an authenticated WebSocket client to invoke unintended internal functions through client-controlled func values in upgrade-func in src/app/server/dispatch-center.js and handleFs in src/app/server/fs.js, exposing Upgrade and fsExport methods that can execute commands, open files, mutate the filesystem, or terminate the process. This issue is fixed in version 3.15.186.

## References
- https://github.com/electerm/electerm/releases/tag/v3.15.186
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73226.json
- https://github.com/electerm/electerm/security/advisories/GHSA-8chw-jwc5-8587
- https://nvd.nist.gov/vuln/detail/CVE-2026-73226
- https://github.com/electerm/electerm/commit/b1729eb67a4cd9cf1182de69dc2c8e051931740f
- https://github.com/electerm/electerm/pull/4447
