# [M] Improper Access Control in wp-graphql

## Summary
Severity: Medium
Advisory: GHSA-w3xg-7q6m-3xwp
CVE: CVE-2019-25060
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-10
Source: https://github.com/advisories/GHSA-w3xg-7q6m-3xwp
Type: github-advisory

## Affected
- Packagist: `wp-graphql/wp-graphql` — affected >=0 <0.3.5

## Details
The WPGraphQL WordPress plugin before 0.3.5 doesn't properly restrict access to information about other users' roles on the affected site. Because of this, a remote attacker could forge a GraphQL query to retrieve the account roles of every user on the site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25060
- https://github.com/wp-graphql/wp-graphql/pull/900
- https://github.com/wp-graphql/wp-graphql
- https://wpscan.com/vulnerability/393be73a-f8dc-462f-8670-f20ab89421fc
