# [M] Potential Heap Out-of-Bounds Read in freerdp_certificate_data_hash_ via Unsafe _snprintf Usage

## Summary
Severity: Medium
Advisory: CVE-2025-68118
Aliases: GHSA-h78c-5cjx-jw6x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-68118
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.20.0, a vulnerability exists in FreeRDP’s certificate handling code on Windows platforms. The function `freerdp_certificate_data_hash_ uses` the Microsoft-specific `_snprintf` function to format certificate cache filenames without guaranteeing NUL termination when truncation occurs. According to Microsoft documentation, `_snprintf` does not append a terminating NUL byte if the formatted output exceeds the destination buffer size. If an attacker controls the hostname value (for example via server redirection or a crafted .rdp file), the resulting filename buffer may not be NUL-terminated. Subsequent string operations performed on this buffer may read beyond the allocated memory region, resulting in a heap-based out-of-bounds read. In default configurations, the connection is typically terminated before sensitive data can be meaningfully exposed, but unintended memory read or a client crash may still occur under certain conditions. Version 3.20.0 has a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68118.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-h78c-5cjx-jw6x
- https://nvd.nist.gov/vuln/detail/CVE-2025-68118
- https://github.com/FreeRDP/FreeRDP/commit/a0b21f992a9de1de2468fc9e600aa2b7a4066307
