# [C] Modular Max Serve has Unsafe Deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-7xcv-9j6c-2fmc
CVE: CVE-2025-60455
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-18
Source: https://github.com/advisories/GHSA-7xcv-9j6c-2fmc
Type: github-advisory

## Affected
- PyPI: `modular` — affected >=0 <25.6.0

## Details
Unsafe Deserialization vulnerability in Modular Max Serve before 25.6, specifically when the "--experimental-enable-kvcache-agent" feature is used allowing attackers to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-60455
- https://github.com/modular/modular/issues/4795
- https://github.com/modular/modular/commit/10620059fb5c47fb0c30e5d21a8ff3b8d622fba4
- https://github.com/modular/modular/commit/b20e749fa892dbe772e890a268002f732164d9f5
- https://github.com/modular/modular/commit/ee9c4ab02345dd30bed8b79771b6909ff1b930a1
- https://github.com/modular/modular
- https://github.com/modular/modular/blame/main/max/serve/kvcache_agent/kvcache_agent.py#L220
- https://www.oligo.security/blog/shadowmq-how-code-reuse-spread-critical-vulnerabilities-across-the-ai-ecosystem
