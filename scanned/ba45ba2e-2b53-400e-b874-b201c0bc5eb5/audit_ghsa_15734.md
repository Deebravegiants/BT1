# [H] Harbor fails to validate the user permissions when updating project configurations

## Summary
Severity: High
Advisory: GHSA-hw28-333w-qxp3
CVE: CVE-2024-22278
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-hw28-333w-qxp3
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=0 <2.9.5
- Go: `github.com/goharbor/harbor` — affected >=2.10.0 <2.10.3

## Details
### Impact
Harbor fails to validate the maintainer role permissions when creating/updating/deleting project configurations - API call:

- PUT /projects/{project_name_or_id}/metadatas/{meta_name}
- POST /projects/{project_name_or_id}/metadatas/{meta_name}
- DELETE /projects/{project_name_or_id}/metadatas/{meta_name}

By sending a request to create/update/delete a metadata with an name that belongs to a project that the currently authenticated and granted to the maintainer role user doesn’t have access to, the attacker could modify configurations in the current project.

BTW: the maintainer role in Harbor was intended for individuals who closely support the project admin in maintaining the project but lack configuration management permissions. However, the maintainer role can utilize the metadata API to circumvent this limitation. It's important to note that any potential attacker must be authenticated and granted a specific project maintainer role to modify configurations, limiting their scope to only that project.


### Patches
Will be fixed in v2.9.5, v2.10.3 and v2.11.0

### Workarounds
There are no workarounds available.

### Credit
Thanks to Ravid Mazon(rmazon@paloaltonetworks.com), Jay Chen (jaychen@paloaltonetworks.com) Palo Alto Networks for reporting this issue.

## References
- https://github.com/goharbor/harbor/security/advisories/GHSA-hw28-333w-qxp3
- https://nvd.nist.gov/vuln/detail/CVE-2024-22278
- https://github.com/goharbor/harbor
- https://pkg.go.dev/vuln/GO-2024-3013
