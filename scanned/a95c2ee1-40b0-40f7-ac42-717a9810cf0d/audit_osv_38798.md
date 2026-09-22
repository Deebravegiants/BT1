# [C] FastGPT: Unauthenticated Remote Code Execution (RCE) via code-server Misconfiguration in agent-sandbox

## Summary
Severity: Critical
Advisory: CVE-2026-42302
Aliases: GHSA-34rc-438g-7w78
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42302
Type: osv

## Details
FastGPT is an AI Agent building platform. From version 4.14.10 to before version 4.14.13, the agent-sandbox component of FastGPT is vulnerable to unauthenticated Remote Code Execution (RCE). The startup script entrypoint.sh initializes code-server with the --auth none flag and binds the service to all network interfaces (0.0.0.0:8080). This configuration allows any user with network access to the port to bypass authentication and gain full control over the sandbox environment. This issue has been patched in version 4.14.13.

## References
- https://github.com/labring/FastGPT/releases/tag/v4.14.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42302.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-34rc-438g-7w78
- https://nvd.nist.gov/vuln/detail/CVE-2026-42302
- https://github.com/labring/FastGPT/commit/9d1cafce9241430fb5bcdd646455055c5f4ae0a4
- https://github.com/labring/FastGPT/pull/6781
