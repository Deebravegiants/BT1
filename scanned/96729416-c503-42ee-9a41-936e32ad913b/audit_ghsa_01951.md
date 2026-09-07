# [M] Authentication bypass in SilverStripe GraphQL

## Summary
Severity: Medium
Advisory: GHSA-mg2g-8pwj-r2j2
CVE: CVE-2020-26136
CWE: CWE-287, CWE-288
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-10
Source: https://github.com/advisories/GHSA-mg2g-8pwj-r2j2
Type: github-advisory

## Affected
- Packagist: `silverstripe/graphql` — affected >=3.0.0 <3.5.0
- Packagist: `silverstripe/graphql` — affected >=4.0.0-alpha1 <4.0.0-alpha2

## Details
The GraphQL module accepts basic-auth as an authentication method by default. This can be used to bypass MFA authentication if the silverstripe/mfa module is installed, which is now a commonly installed module. A users password is still required though.

Basic-auth has been removed as a default authentication method. If desired, it can be re-enabled by adding it to the authenticators key of a schema, or on SilverStripe\Graphql\Auth\Handler

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26136
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/graphql/CVE-2020-26136.yaml
- https://www.silverstripe.org/blog/tag/release
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2020-26136
