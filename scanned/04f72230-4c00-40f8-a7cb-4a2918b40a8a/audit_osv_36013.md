# [H] Velociraptor incorrect Org deletion permissions check

## Summary
Severity: High
Advisory: CVE-2026-18860
CVSS: 8.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-18860
Type: osv

## Details
Velociraptor allows multi-tenant deployments named "Orgs".

By default Velociraptor, uses the ROOT org, but users can create child orgs for other tenants within the same deployment.

Users can have different permissions in each org. To manage Orgs, Velociraptor usually examines the ORG_ADMIN permission on the ROOT org.

This issue results from the Velociraptor server allowing for the deletion of Orgs by incorrectly checking the ORG_ADMIN permission of callers within the calling ORG instead of the ROOT org. However, Org admins of child orgs were able to add this permission to their ACL token within their own org. This allows an administrator in a child org, which is not also an administrator in the ROOT org, to delete other orgs.

## References
- https://github.com/Velocidex/velociraptor/
- https://docs.velociraptor.app/announcements/advisories/cve-2026-18860/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18860.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18860
- https://github.com/Velocidex/velociraptor/commit/dc38bd6a7e12a678cd79e726bdd1ded4eed75967
- https://github.com/Velocidex/velociraptor/releases
