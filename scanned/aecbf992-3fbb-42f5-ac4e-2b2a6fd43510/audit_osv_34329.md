# [H] Onyxia private helm repository credentials are leaked through unauthenticated API

## Summary
Severity: High
Advisory: CVE-2025-58366
Aliases: GHSA-m773-6vm8-8x6q
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-58366
Type: osv

## Details
Onyxia is a data science environment for kubernetes. In versions 4.6.0 through 4.8.0, Onyxia-API leaked the credentials of private helm repositories in the public (unauthenticated) /public/catalogs endpoint.vOnly instances using private helm repositories (i.e setting username & password in the catalogs configuration) are affected. This is fixed in version 4.9.0.

## References
- https://github.com/InseeFrLab/onyxia-api/releases/tag/v4.9.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58366.json
- https://github.com/InseeFrLab/onyxia/security/advisories/GHSA-m773-6vm8-8x6q
- https://nvd.nist.gov/vuln/detail/CVE-2025-58366
- https://github.com/InseeFrLab/onyxia-api/pull/613
