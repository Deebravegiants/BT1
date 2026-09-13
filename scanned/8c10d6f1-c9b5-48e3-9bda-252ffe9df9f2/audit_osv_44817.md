# [C] electerm before 5.3.15 Arbitrary Command Execution via Unvalidated runGlobalAsync IPC Bridge

## Summary
Severity: Critical
Advisory: CVE-2026-86711
Aliases: GHSA-qc8j-6jr2-qr32
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86711
Type: osv

## Details
electerm before 5.3.15 exposes 40+ main-process functions through an unvalidated Electron IPC handler with no function-name allowlist or sender validation. Renderer-side script execution can invoke openFileWithEditor and other functions with arbitrary arguments to execute system commands in the main process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86711.json
- https://github.com/electerm/electerm/releases/tag/v5.3.15
- https://github.com/electerm/electerm/security/advisories/GHSA-qc8j-6jr2-qr32
- https://nvd.nist.gov/vuln/detail/CVE-2026-86711
- https://www.vulncheck.com/advisories/electerm-before-5.3.15-arbitrary-command-execution-via-unvalidated-runglobalasync-ipc-bridge
- https://github.com/electerm/electerm/issues/4509
- https://github.com/electerm/electerm/commit/b1f880534b8ae066c5d25bbf291ca7437e052750
- https://github.com/electerm/electerm
- https://github.com/electerm/electerm/blob/v5.3.5/src/app/lib/ipc.js
