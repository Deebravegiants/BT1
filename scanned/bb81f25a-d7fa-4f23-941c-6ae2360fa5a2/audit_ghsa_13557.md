# [H] Silverstripe GraphQL has DDOS Vulnerability due to lack of protection against recursive queries

## Summary
Severity: High
Advisory: GHSA-v23w-pppm-jh66
CVE: CVE-2023-40180
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-v23w-pppm-jh66
Type: github-advisory

## Affected
- Packagist: `silverstripe/graphql` — affected >=3.0.0 <3.8.2
- Packagist: `silverstripe/graphql` — affected >=4.0.0 <4.1.3
- Packagist: `silverstripe/graphql` — affected >=4.2.0 <4.2.5
- Packagist: `silverstripe/graphql` — affected >=4.3.0 <4.3.4
- Packagist: `silverstripe/graphql` — affected >=5.0.0 <5.0.3

## Details
### Impact
An attacker could use a recursive graphql query to execute a Distributed Denial of Service attack (DDOS attack) against a website. This mostly affects websites with publicly exposed graphql schemas.

If your Silverstripe CMS project does not expose a public facing graphql schema, a user account is required to trigger the DDOS attack. If your site is hosted behind a content delivery network (CDN), such as Imperva or CloudFlare, this may further mitigate the risk.

The fix includes some new configuration options which you might want to tweak for your project, based on your own requirements. See the documentation in the references for details.

### Patches
Patched in [3.8.2](https://github.com/silverstripe/silverstripe-graphql/releases/tag/3.8.2), [4.1.3](https://github.com/silverstripe/silverstripe-graphql/releases/tag/4.1.3), [4.2.5](https://github.com/silverstripe/silverstripe-graphql/releases/tag/4.2.5), [4.3.4](https://github.com/silverstripe/silverstripe-graphql/releases/tag/4.3.4), [5.0.3](https://github.com/silverstripe/silverstripe-graphql/releases/tag/5.0.3)

### References
- [CVE-2023-40180 on silverstripe.org](https://www.silverstripe.org/download/security-releases/CVE-2023-40180)
- [Documentation about protection against recursive or complex queries for silverstripe/graphql 4.x/5.x](https://docs.silverstripe.org/en/developer_guides/graphql/security_and_best_practices/recursive_or_complex_queries)
- [Documentation about protection against recursive or complex queries for silverstripe/graphql 3.x](https://github.com/silverstripe/silverstripe-graphql/tree/3.8#recursive-or-complex-queries)

### Reported by
Jason Nguyen from phew (https://phew.co.nz/)

## References
- https://github.com/silverstripe/silverstripe-graphql/security/advisories/GHSA-v23w-pppm-jh66
- https://nvd.nist.gov/vuln/detail/CVE-2023-40180
- https://github.com/silverstripe/silverstripe-graphql/commit/f6d5976ec4608e51184b0db1ee5b9e9a99d2501c
- https://docs.silverstripe.org/en/developer_guides/graphql/security_and_best_practices/recursive_or_complex_queries
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/graphql/CVE-2023-40180.yaml
- https://github.com/silverstripe/silverstripe-graphql
- https://github.com/silverstripe/silverstripe-graphql/tree/3.8#recursive-or-complex-queries
- https://www.silverstripe.org/download/security-releases/CVE-2023-40180
