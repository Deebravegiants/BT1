# [C] PraisonAI Affected by Untrusted Remote Template Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-40154
Aliases: GHSA-pv9q-275h-rh7x, PYSEC-2026-476
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-40154
Type: osv

## Details
PraisonAI is a multi-agent teams system. Prior to 4.5.128, PraisonAI treats remotely fetched template files as trusted executable code without integrity verification, origin validation, or user confirmation, enabling supply chain attacks through malicious templates. This vulnerability is fixed in 4.5.128.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40154.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-pv9q-275h-rh7x
- https://nvd.nist.gov/vuln/detail/CVE-2026-40154
