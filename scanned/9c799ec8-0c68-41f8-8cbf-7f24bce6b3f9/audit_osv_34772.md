# [M] grist-core has insufficient access control in endpoints for comparisons between documents and versions

## Summary
Severity: Medium
Advisory: CVE-2025-64753
Aliases: GHSA-3v78-cw58-v685
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-13
Source: https://osv.dev/vulnerability/CVE-2025-64753
Type: osv

## Details
grist-core is a spreadsheet hosting server. Prior to version 1.7.7, a user with only partial read access to a document could still access endpoints listing hashes for versions of that document and receive a full list of changes between versions, even if those changes contained cells, columns, or tables to which the user was not supposed to have read access. This was fixed in version 1.7.7 by restricting the `/compare` endpoint to users with full read access. As a workaround, remove sensitive document history using the `/states/remove` endpoint. Another possibility is to block the `/compare` endpoint.

## References
- https://github.com/gristlabs/grist-core/releases/tag/v1.7.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64753.json
- https://github.com/gristlabs/grist-core/security/advisories/GHSA-3v78-cw58-v685
- https://nvd.nist.gov/vuln/detail/CVE-2025-64753
