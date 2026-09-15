# [C] Plandex 2.2.1 Path Traversal via ApplyFiles

## Summary
Severity: Critical
Advisory: CVE-2026-85690
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85690
Type: osv

## Details
Plandex 2.2.1 contains a path traversal vulnerability in the ApplyFiles function that allows attackers to write files outside the project directory. Attackers can influence model output through poisoned repository files or attacker-controlled context to write to arbitrary locations like shell rc or cron files, achieving code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85690.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85690
- https://www.vulncheck.com/advisories/plandex-2.2.1-path-traversal-via-applyfiles
- https://github.com/plandex-ai/plandex/issues/352
- https://github.com/plandex-ai/plandex
- https://github.com/plandex-ai/plandex/blob/cli/v2.2.1/app/cli/lib/apply.go
