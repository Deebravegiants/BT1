# [M] Dify Allows Insecure User Role Access Control for APP DSL Exporting

## Summary
Severity: Medium
Advisory: CVE-2025-32790
Aliases: GHSA-jp6m-v4gw-5vgp
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-32790
Type: osv

## Details
Dify is an open-source LLM app development platform. In versions 0.6.8 and prior, a vulnerability was identified in the DIFY AI where normal users are improperly granted permissions to export APP DSL. The feature in '/export' should only allow administrator users to export DSL. A workaround for this vulnerability involves updating the access control mechanisms to enforce stricter user role permissions and implementing role-based access controls (RBAC) to ensure that only users with admin privileges can export the APP DSL. This vulnerability is fixed in 0.6.13.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32790.json
- https://github.com/langgenius/dify/security/advisories/GHSA-jp6m-v4gw-5vgp
- https://nvd.nist.gov/vuln/detail/CVE-2025-32790
- https://github.com/langgenius/dify/commit/59ad091e69736bc9dc1a3bace62ec0a232346246
- https://github.com/langgenius/dify/pull/5841
