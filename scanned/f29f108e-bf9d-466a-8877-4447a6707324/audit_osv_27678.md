# [M] discourse-group-membership-ip-block is exposing potentially sensitive custom fields

## Summary
Severity: Medium
Advisory: CVE-2024-24755
Aliases: GHSA-r38c-cp8w-664m
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-02-01
Source: https://osv.dev/vulnerability/CVE-2024-24755
Type: osv

## Details
discourse-group-membership-ip-block is a discourse plugin that adds support for adding users to groups based on their IP address. discourse-group-membership-ip-block was sending all group custom fields to the client, including group custom fields from other plugins which may expect their custom fields to remain secret.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24755.json
- https://github.com/discourse/discourse-group-membership-ip-block/security/advisories/GHSA-r38c-cp8w-664m
- https://nvd.nist.gov/vuln/detail/CVE-2024-24755
- https://github.com/discourse/discourse-group-membership-ip-block/commit/b394d61b0bdfd18a2d8310aa5cf26cccf8bd31c1
