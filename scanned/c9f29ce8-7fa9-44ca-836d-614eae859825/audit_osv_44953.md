# [H] Relative path traversal in the generated file manifest cleanup component in projen

## Summary
Severity: High
Advisory: CVE-2026-89065
Aliases: GHSA-7p65-6x86-v7f3
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-89065
Type: osv

## Details
Relative path traversal in the generated file manifest cleanup component in projen before 0.101.37 might allow context-dependent attackers to recursively delete files and directories outside the project directory that are writable by the environment running projen, via crafted entries in the version-controlled generated file manifest that is consumed during project synthesis.



To remediate this issue, users should upgrade to version 0.101.37. The corrected containment check is automatically applied by the projen runtime next time you run it.

## References
- https://aws.amazon.com/security/security-bulletins/2026-108-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/89xxx/CVE-2026-89065.json
- https://github.com/projen/projen/releases/tag/v0.101.37
- https://github.com/projen/projen/security/advisories/GHSA-7p65-6x86-v7f3
- https://nvd.nist.gov/vuln/detail/CVE-2026-89065
