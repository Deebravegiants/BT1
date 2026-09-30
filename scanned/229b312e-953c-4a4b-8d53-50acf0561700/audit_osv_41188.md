# [M] Vibe-Trading < 0.1.10 - Path Traversal via Persistent Memory Type

## Summary
Severity: Medium
Advisory: CVE-2026-58173
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58173
Type: osv

## Details
Vibe-Trading before 0.1.10 contains a path traversal vulnerability that allows attackers to write files outside the intended memory root directory by supplying a malicious memory_type value containing path traversal sequences through the remember tool. Attackers can manipulate the memory_type parameter in the persistent memory store to cause the application to write arbitrary Markdown files to unintended locations on the filesystem.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58173.json
- https://github.com/HKUDS/Vibe-Trading/releases/tag/v0.1.10
- https://nvd.nist.gov/vuln/detail/CVE-2026-58173
- https://www.vulncheck.com/advisories/vibe-trading-path-traversal-via-persistent-memory-type
- https://github.com/HKUDS/Vibe-Trading/pull/257
- https://github.com/HKUDS/Vibe-Trading
