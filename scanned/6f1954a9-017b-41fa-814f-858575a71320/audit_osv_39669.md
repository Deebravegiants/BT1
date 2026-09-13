# [C] Flowise: DatasetRow create+update mass-assignment allows cross-workspace row takeover

## Summary
Severity: Critical
Advisory: CVE-2026-46478
Aliases: GHSA-7j65-65cr-6644
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-46478
Type: osv

## Details
Flowise is a drag & drop user interface to build a customized large language model flow. Prior to version 3.1.2, DatasetRow create and update mass-assignment allows cross-workspace row takeover. This issue has been patched in version 3.1.2.

## References
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.1.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46478.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-7j65-65cr-6644
- https://nvd.nist.gov/vuln/detail/CVE-2026-46478
