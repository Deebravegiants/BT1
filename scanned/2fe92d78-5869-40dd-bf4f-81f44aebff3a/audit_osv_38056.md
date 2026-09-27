# [C] ByteDance DeerFlow LocalSandboxProvider Host Bash Escape

## Summary
Severity: Critical
Advisory: CVE-2026-34430
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-34430
Type: osv

## Details
ByteDance DeerFlow versions prior to commit 92c7a20 contain a sandbox escape vulnerability in bash tool handling that allows attackers to execute arbitrary commands on the host system by bypassing regex-based validation using shell features such as directory changes and relative paths. Attackers can exploit the incomplete shell semantics modeling to read and modify files outside the sandbox boundary and achieve arbitrary command execution through subprocess invocation with shell interpretation enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34430.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34430
- https://www.vulncheck.com/advisories/bytedance-deerflow-localsandboxprovider-host-bash-escape
- https://github.com/bytedance/deer-flow/pull/1547
- https://github.com/bytedance/deer-flow/commit/92c7a20cb74addc3038d2131da78f2e239ef542e
- https://github.com/bytedance/deer-flow
