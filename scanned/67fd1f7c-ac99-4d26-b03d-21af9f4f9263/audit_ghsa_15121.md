# [M] View permissions are bypassed for paginated lists of ORM data

## Summary
Severity: Medium
Advisory: GHSA-jgph-w8rh-xf5p
CVE: CVE-2023-44401
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-01-23
Source: https://github.com/advisories/GHSA-jgph-w8rh-xf5p
Type: github-advisory

## Affected
- Packagist: `silverstripe/graphql` — affected >=4.0.0 <4.3.7
- Packagist: `silverstripe/graphql` — affected >=5.0.0 <5.1.3

## Details
### Impact
`canView` permission checks are bypassed for ORM data in paginated GraphQL query results where the total number of records is greater than the number of records per page.

Note that this also affects GraphQL queries which have a limit applied, even if the query isn’t paginated per se.

This has been fixed by ensuring no new records are pulled in from the database after performing `canView` permission checks for each page of results. This may result in some pages in your query results having less than the maximum number of records per page even when there are more pages of results.

This behaviour is consistent with how pagination works in other areas of Silverstripe CMS, such as in `GridField`, and is a result of having to perform permission checks in PHP rather than in the database directly.

You can choose to disable these permission checks by disabling the `CanViewPermission` plugin following the instructions in [overriding default plugins](https://docs.silverstripe.org/en/5/developer_guides/graphql/plugins/overview/#overriding-default-plugins).

Note that this vulnerability does not affect version 3.x.

**Base CVSS:** [5.3](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N/E:F/RL:O/RC:C&version=3.1)
**Reported by:** Eduard Briem from Hothouse Creative, Nelson

### References
https://www.silverstripe.org/download/security-releases/CVE-2023-44401

## References
- https://github.com/silverstripe/silverstripe-graphql/security/advisories/GHSA-jgph-w8rh-xf5p
- https://nvd.nist.gov/vuln/detail/CVE-2023-44401
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/graphql/CVE-2023-44401.yaml
- https://github.com/silverstripe/silverstripe-graphql
- https://www.silverstripe.org/download/security-releases/CVE-2023-44401
