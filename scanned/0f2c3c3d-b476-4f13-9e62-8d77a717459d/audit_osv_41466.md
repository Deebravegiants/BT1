# [C] PraisonAI before 4.6.78 Code Injection via API deployment generator

## Summary
Severity: Critical
Advisory: CVE-2026-61433
Aliases: GHSA-79fv-7hq9-w7xg
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-61433
Type: osv

## Details
PraisonAI before 4.6.78 fails to safely encode deployment configuration values when generating Python source code for API servers. Attackers can inject arbitrary Python expressions through the deploy.api.host and agents_file configuration parameters that execute when the generated server starts or handles requests.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61433.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-79fv-7hq9-w7xg
- https://nvd.nist.gov/vuln/detail/CVE-2026-61433
- https://www.vulncheck.com/advisories/praisonai-before-code-injection-via-api-deployment-generator
- https://github.com/MervinPraison/PraisonAI/commit/1620b49f36945d8cc8ee5635b906c960df5097a0
