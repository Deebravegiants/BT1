# [H] Craft CMS: GraphQL Asset Mutation Privilege Escalation

## Summary
Severity: High
Advisory: GHSA-fxp3-g6gw-4r4v
CVE: CVE-2026-25497
CWE: CWE-269, CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-fxp3-g6gw-4r4v
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.0-beta.1
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.0-beta.1

## Details
There is a Privilege Escalation vulnerability in Craft CMS’s GraphQL API that allows an authenticated user with write access to one asset volume to escalate their privileges and modify/transfer assets belonging to any other volume, including restricted or private volumes to which they should not have access.

## Summary:

Type: Privilege Escalation (CWE-269)
Affected: Craft CMS 5.x (likely affects 4.x and 3.x as well)
Location: `src/gql/resolvers/mutations/Asset.php lines 57-107`

## Root Cause:

The saveAsset GraphQL mutation validates authorization against the schema-resolved volume but fetches the target asset by ID without verifying that the asset belongs to the authorized volume. This allows unauthorized cross-volume asset modification and transfer.

## Impact:

- Transfer confidential assets from private volumes to public volumes (data exfiltration)
- Modify asset metadata in restricted volumes
- Bypass multi-tenant isolation in shared hosting environments

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-fxp3-g6gw-4r4v
- https://nvd.nist.gov/vuln/detail/CVE-2026-25497
- https://github.com/craftcms/cms/commit/ac7edf868c1a81fd9c4dc49d3b3edf1cce113409
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.17.0-beta.1
- https://github.com/craftcms/cms/releases/tag/5.8.22
- https://github.com/craftcms/cms/releases/tag/5.9.0-beta.1
