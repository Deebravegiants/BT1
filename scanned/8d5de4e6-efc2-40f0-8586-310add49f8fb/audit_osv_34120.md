# [C] Kanboard Authenticated Admin Remote Code Execution via Unsafe Deserialization of Events

## Summary
Severity: Critical
Advisory: CVE-2025-55010
Aliases: GHSA-359x-c69j-q64r
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-08-12
Source: https://osv.dev/vulnerability/CVE-2025-55010
Type: osv

## Details
Kanboard is project management software that focuses on the Kanban methodology. Prior to version 1.2.47, an unsafe deserialization vulnerability in the ProjectEventActvityFormatter allows admin users the ability to instantiate arbitrary php objects by modifying the event["data"] field in the project_activities table. A malicious actor can update this field to use a php gadget to write a web shell into the /plugins folder, which then gives remote code execution on the host system. This issue has been patched in version 1.2.47.

## References
- https://github.com/kanboard/kanboard/blob/b033c0e0f982f8158e240bce8ab54c29727f8efe/app/Formatter/ProjectActivityEventFormatter.php#L43-L57
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55010.json
- https://github.com/kanboard/kanboard/security/advisories/GHSA-359x-c69j-q64r
- https://nvd.nist.gov/vuln/detail/CVE-2025-55010
- https://github.com/kanboard/kanboard/commit/7148ac092e5db6b33e0fc35e04bca328d96c1f6f
