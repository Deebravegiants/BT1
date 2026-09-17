# [H] CVE-2026-11576

## Summary
Severity: High
Advisory: CVE-2026-11576
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-11576
Type: osv

## Details
The security fix for CVE-2025-0728 in eclipse-threadx NetX Duo refactors error handling in the HTTP server PUT process to use a shared cleanup label, but this unified cleanup path unconditionally calls fx_file_close() even when the file was never successfully opened. Multiple error branches jump to the shared cleanup label before any file open operation has occurred, causing fx_file_close() to operate on an uninitialized file handle, leading to undefined behavior, double-close issues, or memory corruption.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/123
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11576.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11576
- https://github.com/eclipse-threadx/netxduo
