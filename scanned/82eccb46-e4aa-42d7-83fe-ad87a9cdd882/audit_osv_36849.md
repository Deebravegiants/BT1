# [C] AutoGPT Affected by Remote Code Execution via Dynamic Module Import in Block Loading (__import__)

## Summary
Severity: Critical
Advisory: CVE-2026-26020
Aliases: GHSA-4crw-9p35-9x54
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/CVE-2026-26020
Type: osv

## Details
AutoGPT is a platform that allows users to create, deploy, and manage continuous artificial intelligence agents that automate complex workflows. Prior to 0.6.48, an authenticated user could achieve Remote Code Execution (RCE) on the backend server by embedding a disabled block inside a graph. The BlockInstallationBlock — a development tool capable of writing and importing arbitrary Python code — was marked disabled=True, but graph validation did not enforce this flag. This allowed any authenticated user to bypass the restriction by including the block as a node in a graph, rather than calling the block's execution endpoint directly (which did enforce the flag). This vulnerability is fixed in 0.6.48.

## References
- https://github.com/Significant-Gravitas/AutoGPT/releases/tag/autogpt-platform-beta-v0.6.48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26020.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-4crw-9p35-9x54
- https://nvd.nist.gov/vuln/detail/CVE-2026-26020
- https://github.com/Significant-Gravitas/AutoGPT/commit/062fe1aa709217136b896c8b950e0f04435afb32
