# [H] Silverstripe CSRF Protection Bypass via GraphQL

## Summary
Severity: High
Advisory: GHSA-fx37-56v6-85q6
CVE: CVE-2019-12437
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fx37-56v6-85q6
Type: github-advisory

## Affected
- Packagist: `silverstripe/graphql` — affected >=2.0.0 <2.0.5
- Packagist: `silverstripe/graphql` — affected >=3.1.0 <3.1.2

## Details
In SilverStripe/GraphQL prior to 2.0.5 and 3.1.2, the previous fix for SS-2018-007 does not completely mitigate the risk of CSRF in GraphQL mutations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12437
- https://github.com/silverstripe/silverstripe-graphql/commit/3c1dd6b839b7c0e2cbc85074bb5840ebded6097c
- https://github.com/silverstripe/silverstripe-graphql/commit/db28f3075ae2335905f43ac808e9177497e354ff
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/graphql/CVE-2019-12437.yaml
- https://github.com/silverstripe/silverstripe-graphql
- https://www.silverstripe.org/download/security-releases/cve-2019-12437
