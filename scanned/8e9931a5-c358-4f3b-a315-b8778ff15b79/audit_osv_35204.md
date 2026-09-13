# [H] LibreChat has Insufficient Access Control for Agent Files

## Summary
Severity: High
Advisory: CVE-2025-69220
Aliases: GHSA-xcmf-rpmh-hg59
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:L)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2025-69220
Type: osv

## Details
LibreChat is a ChatGPT clone with additional features. Version 0.8.1-rc2 does not enforce proper access control for file uploads to an agents file context and file search. An authenticated attacker with access to the agent ID can change the behavior of arbitrary agents by uploading new files to the file context or file search, even if they have no permissions for this agent. This issue is fixed in version 0.8.2-rc2.

## References
- https://cwe.mitre.org/data/definitions/284.html
- https://cwe.mitre.org/data/definitions/862.html
- https://github.com/danny-avila/LibreChat/releases/tag/v0.8.2-rc2
- https://owasp.org/Top10/A01_2021-Broken_Access_Control
- https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/05-Authorization_Testing/02-Testing_for_Bypassing_Authorization_Schema.html
- https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/OWASP_Application_Security_Verification_Standard_5.0.0_en.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69220.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-xcmf-rpmh-hg59
- https://nvd.nist.gov/vuln/detail/CVE-2025-69220
- https://github.com/danny-avila/LibreChat/commit/4b9c6ab1cb9de626736de700c7981f38be08d237
