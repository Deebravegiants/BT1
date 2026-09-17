# [H] BIT-openproject-2023-33960

## Summary
Severity: High
Advisory: BIT-openproject-2023-33960
Aliases: CVE-2023-33960, GHSA-xjfc-fqm3-95q8
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-openproject-2023-33960
Type: osv

## Affected
- Bitnami: `openproject` — affected >=0 <12.5.6

## Details
OpenProject is web-based project management software. For any OpenProject installation, a `robots.txt` file is generated through the server to denote which routes shall or shall not be accessed by crawlers. These routes contain project identifiers of all public projects in the instance. Prior to version 12.5.6, even if the entire instance is marked as `Login required` and prevents all truly anonymous access, the `/robots.txt` route remains publicly available.Version 12.5.6 has a fix for this issue. Alternatively, users can download a patchfile to apply the patch to any OpenProject version greater than 10.0 As a workaround, one may mark any public project as non-public and give anyone in need of access to the project a membership.

## References
- https://community.openproject.org/wp/48324
- https://github.com/opf/openproject/pull/12708
- https://github.com/opf/openproject/releases/tag/v12.5.6
- https://github.com/opf/openproject/security/advisories/GHSA-xjfc-fqm3-95q8
- https://patch-diff.githubusercontent.com/raw/opf/openproject/pull/12708.patch
