# [H] Sandboxie-Plus: Sandboxie APC Injection Sandbox Escape

## Summary
Severity: High
Advisory: CVE-2026-45313
Aliases: GHSA-rmv3-fhg3-75xh
CVSS: 7.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-45313
Type: osv

## Details
Sandboxie-Plus is an open source sandbox-based isolation software for Windows. Prior to 1.17.6, GuiServer::WndHookRegisterSlave in Sandboxie/core/svc/GuiServer.cpp stores attacker-supplied hthread and hproc fields from a GUI_WND_HOOK_REGISTER request without validating that the thread belongs to the sandboxed process or that the function pointer is in the caller address space, and GuiServer::WndHookNotifySlave then calls OpenThread(THREAD_SET_CONTEXT, FALSE, whk->hthread) and QueueUserAPC((PAPCFUNC)whk->hproc, hThread, (ULONG_PTR)req->threadid) as SYSTEM, allowing a sandboxed process to execute arbitrary code in an unsandboxed host process. This issue is fixed in version 1.17.6.

## References
- https://github.com/sandboxie-plus/Sandboxie/releases/tag/v1.17.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45313.json
- https://github.com/sandboxie-plus/Sandboxie/security/advisories/GHSA-rmv3-fhg3-75xh
- https://nvd.nist.gov/vuln/detail/CVE-2026-45313
