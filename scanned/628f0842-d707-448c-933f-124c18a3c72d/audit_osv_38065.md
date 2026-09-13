# [C] Sandboxie-Plus ProcessServer boxname stack buffer overflows via unterminated wide string copy

## Summary
Severity: Critical
Advisory: CVE-2026-34462
Aliases: GHSA-9cjg-vh9m-hhx4
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-34462
Type: osv

## Details
Sandboxie-Plus is an open source sandbox-based isolation software for Windows. In versions 1.17.2 and earlier, several ProcessServer handlers (KillAllHandler, SuspendAllHandler, and RunSandboxedHandler) copy a WCHAR boxname[34] field from request structures into WCHAR[40] stack buffers using wcscpy without verifying null termination. Because the service pipe accepts variable-length packets larger than the request structure, an attacker can fill the boxname field with non-zero data and append additional controlled wide characters after the structure. wcscpy then reads past the fixed field and overflows the destination stack buffer. The service pipe is created with a NULL DACL, allowing any local process to connect, and the unsafe copy occurs before authorization checks. This can lead to a crash of the SbieSvc service or potential code execution as SYSTEM. This issue has been fixed in version 1.17.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34462.json
- https://github.com/sandboxie-plus/Sandboxie/security/advisories/GHSA-9cjg-vh9m-hhx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-34462
