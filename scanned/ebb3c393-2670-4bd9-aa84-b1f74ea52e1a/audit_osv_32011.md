# [C] WeGIA Allows Arbitrary File Upload with Remote Code Execution (RCE)

## Summary
Severity: Critical
Advisory: CVE-2025-22133
Aliases: GHSA-mjgr-2jxv-v8qf
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-01-07
Source: https://osv.dev/vulnerability/CVE-2025-22133
Type: osv

## Details
WeGIA is a web manager for charitable institutions. Prior to 3.2.8, a critical vulnerability was identified in the /WeGIA/html/socio/sistema/controller/controla_xlsx.php endpoint. The endpoint accepts file uploads without proper validation, allowing the upload of malicious files, such as .phar, which can then be executed by the server. This vulnerability is fixed in 3.2.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22133.json
- https://github.com/nilsonLazarin/WeGIA/security/advisories/GHSA-mjgr-2jxv-v8qf
- https://nvd.nist.gov/vuln/detail/CVE-2025-22133
- https://github.com/nilsonLazarin/WeGIA/commit/a08f04de96d3caec85496d7a89a5b82d1960d9dd
