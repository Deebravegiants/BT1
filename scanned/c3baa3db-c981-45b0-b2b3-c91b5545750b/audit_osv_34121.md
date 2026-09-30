# [M] Kanboard Path Traversal in File Write via Task File Upload Api

## Summary
Severity: Medium
Advisory: CVE-2025-55011
Aliases: GHSA-26f4-rx96-xc55
CVSS: 6.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-08-12
Source: https://osv.dev/vulnerability/CVE-2025-55011
Type: osv

## Details
Kanboard is project management software that focuses on the Kanban methodology. Prior to version 1.2.47, the createTaskFile method in the API does not validate whether the task_id parameter is a valid task id, nor does it check for path traversal. As a result, a malicious actor could write a file anywhere on the system the app user controls. The impact is limited due to the filename being hashed and having no extension. This issue has been patched in version 1.2.47.

## References
- https://github.com/kanboard/kanboard/blob/b2e35ac520add67cff792aab960b3c002c48e3d0/app/Api/Procedure/TaskFileProcedure.php#L47-L57
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55011.json
- https://github.com/kanboard/kanboard/security/advisories/GHSA-26f4-rx96-xc55
- https://nvd.nist.gov/vuln/detail/CVE-2025-55011
- https://github.com/kanboard/kanboard/commit/523a6135e944b6884c091a3fd7605af8ef133681
