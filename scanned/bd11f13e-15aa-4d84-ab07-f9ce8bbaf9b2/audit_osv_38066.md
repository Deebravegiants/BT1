# [C] Sandboxie-Plus NamedPipeServer OpenHandler stack overflow via unterminated server field

## Summary
Severity: Critical
Advisory: CVE-2026-34464
Aliases: GHSA-cf8x-f33g-vwfg
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-34464
Type: osv

## Details
Sandboxie-Plus is an open source sandbox-based isolation software for Windows. In versions 1.17.2 and earlier, NamedPipeServer::OpenHandler copies the server field from NAMED_PIPE_OPEN_REQ into a fixed WCHAR pipename[160] stack buffer using wcscat without verifying null termination. The handler only enforces a minimum packet size, and since the service pipe accepts variable-length messages, a sandboxed caller can fill the server[48] field with non-zero data and append additional controlled wide characters after the structure. wcscat then reads past the fixed field and overflows the stack buffer in the SYSTEM service. This message is restricted to sandboxed callers, making it a sandbox escape vector. This can lead to a crash of the SbieSvc service or potential code execution as SYSTEM. This issue has been fixed in version 1.17.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34464.json
- https://github.com/sandboxie-plus/Sandboxie/security/advisories/GHSA-cf8x-f33g-vwfg
- https://nvd.nist.gov/vuln/detail/CVE-2026-34464
