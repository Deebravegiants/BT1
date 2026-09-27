# [H] MISP Sharing Group Authorization Bypass via Omitted Distribution Parameter

## Summary
Severity: High
Advisory: CVE-2026-85533
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85533
Type: osv

## Details
An authorization flaw in MISP allowed an authenticated user to submit a sharing_group_id without verifying that the user was authorized to use the referenced Sharing Group.

In several attribute and Galaxy Cluster creation and editing workflows, validation of the submitted Sharing Group was performed only when the request explicitly set the distribution field to 4 ("Sharing Group"). An attacker could therefore craft a request containing a sharing_group_id while omitting the distribution parameter, or otherwise avoiding the distribution == 4 condition, causing the Sharing Group authorization check to be skipped.

This could allow a user with permission to create or modify the affected MISP objects to associate data with a Sharing Group that they are not authorized to use. Depending on the affected object's existing distribution settings and subsequent processing, this could bypass intended information-sharing boundaries and result in unauthorized placement or distribution of data to members of another Sharing Group.

The issue affected attribute attachment and editing operations as well as Galaxy Cluster creation and editing. The fix ensures that authorization is performed whenever a non-empty sharing_group_id is submitted, independently of the distribution parameter. It also centralizes the authorization decision in SharingGroup::canUse() and explicitly rejects empty Sharing Group identifiers rather than allowing them to be interpreted as an unrestricted query.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85533.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85533
- https://github.com/MISP/MISP/commit/9b1363955
- https://github.com/MISP/MISP
