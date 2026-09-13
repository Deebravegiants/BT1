# [C] PraisonAI before 4.6.78 Allowlist Bypass via find -exec

## Summary
Severity: Critical
Advisory: CVE-2026-61434
Aliases: GHSA-cv3g-hj65-pcfh
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-61434
Type: osv

## Details
PraisonAI versions before 4.6.78 contain an allowlist bypass vulnerability in shell command execution that allows attackers to execute restricted commands via find's built-in -exec, -execdir, and -delete actions. Attackers can craft find commands with these built-in actions to read blocked files, delete files, or execute non-allowlisted binaries without triggering shell metacharacter filters.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61434.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-cv3g-hj65-pcfh
- https://nvd.nist.gov/vuln/detail/CVE-2026-61434
- https://www.vulncheck.com/advisories/praisonai-before-allowlist-bypass-via-find-exec
