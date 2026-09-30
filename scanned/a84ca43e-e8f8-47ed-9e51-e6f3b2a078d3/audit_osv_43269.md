# [M] Scriban 3.0.0 through 7.2.5 Denial of Service via ScriptRange.Multiply

## Summary
Severity: Medium
Advisory: CVE-2026-73060
Aliases: GHSA-89cf-6hmv-8rxm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-16
Source: https://osv.dev/vulnerability/CVE-2026-73060
Type: osv

## Details
Scriban versions from 3.0.0 through 7.2.5 contain a denial of service vulnerability in the ScriptRange.Multiply operator that bypasses LoopLimit when the left operand is a lazy sequence. Attackers can supply templates with array multiplication on lazy sequences to execute billions of uncharged iterations, pinning CPU cores and exhausting garbage collection resources even when LoopLimit is set to 1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73060.json
- https://github.com/scriban/scriban/security/advisories/GHSA-89cf-6hmv-8rxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-73060
- https://www.vulncheck.com/advisories/scriban-through-denial-of-service-via-scriptrange-multiply
- https://github.com/scriban/scriban/commit/205ca6a7c2349d3d388bd5f1f7729ee198c0d5e5
- https://github.com/scriban/scriban/commit/c3f03bfc912e14b306a01a03e611f606b05f9c33
