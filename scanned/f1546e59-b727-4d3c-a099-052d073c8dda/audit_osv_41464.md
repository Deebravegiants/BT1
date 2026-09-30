# [M] PraisonAI before 4.6.78 Path Traversal via ContextGatherer

## Summary
Severity: Medium
Advisory: CVE-2026-61431
Aliases: GHSA-q7m5-3jmv-vm48
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-61431
Type: osv

## Details
PraisonAI before 4.6.78 contains a path traversal vulnerability in ContextGatherer that fails to validate include paths in .praisoncontext and .praisoninclude files. Attackers can supply absolute paths or parent directory traversal sequences to read arbitrary files outside the workspace and include their contents in the generated context bundle.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61431.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-q7m5-3jmv-vm48
- https://nvd.nist.gov/vuln/detail/CVE-2026-61431
- https://www.vulncheck.com/advisories/praisonai-before-path-traversal-via-contextgatherer
- https://github.com/MervinPraison/PraisonAI/commit/1620b49f36945d8cc8ee5635b906c960df5097a0
