# [M] CVE-2025-54558

## Summary
Severity: Medium
Advisory: CVE-2025-54558
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-54558
Type: osv

## Details
OpenAI Codex CLI before 0.9.0 auto-approves ripgrep (aka rg) execution even with the --pre or --hostname-bin or --search-zip or -z flag.

## References
- https://github.com/openai/codex/compare/rust-v0.8.0...rust-v0.9.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54558.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-54558
- https://github.com/openai/codex/commit/6cf4b96f9dbbef8a94acc1ff703eb118481514d8
- https://github.com/openai/codex/pull/1644
