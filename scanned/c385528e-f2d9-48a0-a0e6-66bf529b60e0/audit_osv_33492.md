# [H] Dify Allows Unauthorized Access and Modification of APP Orchestration

## Summary
Severity: High
Advisory: CVE-2025-43862
Aliases: GHSA-6pw4-jqhv-3626
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2025-04-25
Source: https://osv.dev/vulnerability/CVE-2025-43862
Type: osv

## Details
Dify is an open-source LLM app development platform. Prior to version 0.6.12, a normal user is able to access and modify APP orchestration, even though the web UI of APP orchestration is not presented for a normal user. This access control flaw allows non-admin users to make unauthorized access and changes on the APPSs. This issue has been patched in version 0.6.12. A workaround for this vulnerability involves updating the the access control mechanisms to enforce stricter user role permissions and implementing role-based access controls (RBAC) to ensure that only users with admin privileges can access Orchestration of the APPs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/43xxx/CVE-2025-43862.json
- https://github.com/langgenius/dify/security/advisories/GHSA-6pw4-jqhv-3626
- https://nvd.nist.gov/vuln/detail/CVE-2025-43862
- https://github.com/langgenius/dify/pull/5266
