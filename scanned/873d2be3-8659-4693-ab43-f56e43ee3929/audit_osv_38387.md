# [M] MaxKB: Sandbox escape via ctypes and unhooked SYS_pkey_mprotect

## Summary
Severity: Medium
Advisory: CVE-2026-39421
Aliases: GHSA-9c6w-j7w5-3gf7
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-39421
Type: osv

## Details
MaxKB is an open-source AI assistant for enterprise. Versions 2.7.1 and below contain a sandbox escape vulnerability in the ToolExecutor component. By leveraging Python's ctypes library to execute raw system calls, an authenticated attacker with workspace privileges can bypass the LD_PRELOAD-based sandbox.so module to achieve arbitrary code execution via direct kernel system calls, enabling full network exfiltration and container compromise. The library intercepts critical standard system functions such as execve, system, connect, and open. It also intercepts mprotect to prevent PROT_EXEC (executable memory) allocations within the sandboxed Python processes, but pkey_mprotect is not blocked. This issue has been fixed in version 2.8.0.

## References
- https://github.com/1Panel-dev/MaxKB/releases/tag/v2.8.0
- https://github.com/1Panel-dev/MaxKB/security/advisories/GHSA-9c6w-j7w5-3gf7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39421.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39421
- https://github.com/1Panel-dev/MaxKB/commit/479701a4d2e6059506bad0057a66bed91abb5aef
