# [C] OpenProject: IDOR through /projects/<A>/settings/project_storages/<A_ps_id> via PATCH parameter "storages_project_storage[project_folder_id]" leads to Access to Unauthorized Resources

## Summary
Severity: Critical
Advisory: CVE-2026-52782
Aliases: GHSA-3vpx-94qx-xpw6
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-52782
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.3.3 and 17.4.1, there is an IDOR through /projects/<A>/settings/project_storages/<A_ps_id> via PATCH parameter "storages_project_storage[project_folder_id]" leads to Access to Unauthorized Resources. A project-admin in one project can hijack the managed Nextcloud or OneDrive folder of another project on the same storage by writing the victim project's project_folder_id into the attacker's Storages::ProjectStorage row. The next managed-folder sync overwrites the ACL on the referenced folder with the attacker project's user list. This vulnerability is fixed in 17.3.3 and 17.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52782.json
- https://github.com/opf/openproject/security/advisories/GHSA-3vpx-94qx-xpw6
- https://nvd.nist.gov/vuln/detail/CVE-2026-52782
