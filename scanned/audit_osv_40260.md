# [M] OpenProject: Cross-project authorization bypass allows deleting public Calendar and Team Planner queries from unauthorized projects

## Summary
Severity: Medium
Advisory: CVE-2026-52779
Aliases: GHSA-jrx5-px3f-vfq4
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-52779
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.3.3 and 17.4.1, a cross-project IDOR / authorization context confusion in the Calendar and Team Planner modules allows a user with management permissions in one project to delete public Calendar or Team Planner Queries from another project where they do not have the corresponding management permissions. Both modules authorize the request against the project identified by :project_id in the URL, but the actual Query object is loaded later by :id from Query.visible(current_user) without verifying that the loaded Query belongs to the authorized project. As a result, an attacker can use permissions from Project A to delete shared/public Calendar or Team Planner views from Project B, causing integrity impact and limited availability impact for users relying on those shared views. This vulnerability is fixed in 17.3.3 and 17.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52779.json
- https://github.com/opf/openproject/security/advisories/GHSA-jrx5-px3f-vfq4
- https://nvd.nist.gov/vuln/detail/CVE-2026-52779
