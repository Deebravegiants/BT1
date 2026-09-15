# [C] Knowage Contains a Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-59954
Aliases: GHSA-96cv-75hg-xrgq
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P)
Published: 2025-09-29
Source: https://osv.dev/vulnerability/CVE-2025-59954
Type: osv

## Details
Knowage is an open source analytics and business intelligence suite. Versions 8.1.26 and below are vulnerable to Remote Code Exection through using an unsafe org.apache.commons.jxpath.JXPathContext in MetaService.java service. This issue is fixed in version 8.1.27.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59954.json
- https://github.com/KnowageLabs/Knowage-Server/security/advisories/GHSA-96cv-75hg-xrgq
- https://nvd.nist.gov/vuln/detail/CVE-2025-59954
- https://github.com/KnowageLabs/Knowage-Server/commit/1bb60d42557724f7ed24c19df6c5017e169527ca
