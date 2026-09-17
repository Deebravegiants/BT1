# [M] ByteDance DeerFlow Path Traversal and Arbitrary File Write via Bootstrap Mode

## Summary
Severity: Medium
Advisory: CVE-2026-40518
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40518
Type: osv

## Details
ByteDance DeerFlow before commit 2176b2b contains a path traversal and arbitrary file write vulnerability in bootstrap-mode custom-agent creation where the agent name validation is bypassed. Attackers can supply traversal-style values or absolute paths as the agent name to influence directory creation and write files outside the intended custom-agent directory, potentially achieving arbitrary file write on the system subject to filesystem permissions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40518.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40518
- https://www.vulncheck.com/advisories/bytedance-deerflow-path-traversal-and-arbitrary-file-write-via-bootstrap-mode
- https://github.com/bytedance/deer-flow/pull/2274
- https://github.com/bytedance/deer-flow/commit/2176b2bbfccfce25ceee08318813f96d843a13fd
- https://github.com/bytedance/deer-flow
