# [C] Hulumi before v1.3.2 Helper Script Shadowing via Workspace Files

## Summary
Severity: Critical
Advisory: CVE-2026-82862
Aliases: GHSA-mjcg-x5mr-27ww
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82862
Type: osv

## Details
Hulumi versions before v1.3.2 resolve the threat-model helper script from an unsafe root, allowing workspace files to shadow the intended helper script. Attackers can place malicious files in the workspace to execute arbitrary code during local skill execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82862.json
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-mjcg-x5mr-27ww
- https://nvd.nist.gov/vuln/detail/CVE-2026-82862
- https://www.vulncheck.com/advisories/hulumi-before-1.3.2-helper-script-shadowing-via-workspace-files
