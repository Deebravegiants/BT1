# [M] FastGPT Sandbox Vulnerable to Sandbox Bypass

## Summary
Severity: Medium
Advisory: CVE-2025-49131
Aliases: GHSA-f3pf-r3g7-g895
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-06-09
Source: https://osv.dev/vulnerability/CVE-2025-49131
Type: osv

## Details
FastGPT is an open-source project that provides a platform for building, deploying, and operating AI-driven workflows and conversational agents. The Sandbox container (fastgpt-sandbox) is a specialized, isolated environment used by FastGPT to safely execute user-submitted or dynamically generated code in isolation. The sandbox before version 4.9.11 has insufficient isolation and inadequate restrictions on code execution by allowing overly permissive syscalls, which allows attackers to escape the intended sandbox boundaries. Attackers could exploit this to read and overwrite arbitrary files and bypass Python module import restrictions. This is patched in version 4.9.11 by restricting the allowed system calls to a safer subset and additional descriptive error messaging.

## References
- https://github.com/labring/FastGPT/pkgs/container/fastgpt-sandbox
- https://github.com/labring/FastGPT/releases/tag/v4.9.11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49131.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-f3pf-r3g7-g895
- https://nvd.nist.gov/vuln/detail/CVE-2025-49131
- https://github.com/labring/FastGPT/commit/bb810a43a1c70683fab7f5fe993771e930a94426
- https://github.com/labring/FastGPT/pull/4958
