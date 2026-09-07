# [M] Incorrect Access Control vulnerability in api-platform/core

## Summary
Severity: Medium
Advisory: GHSA-974j-wjxx-wggj
CVE: CVE-2019-1000011
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-10-14
Source: https://github.com/advisories/GHSA-974j-wjxx-wggj
Type: github-advisory

## Affected
- Packagist: `api-platform/core` — affected >=2.2.0 <2.2.10
- Packagist: `api-platform/core` — affected >=2.3.0 <2.3.6

## Details
API Platform version from 2.2.0 to 2.3.5 contains an Incorrect Access Control vulnerability in GraphQL delete mutations that can result in a user authorized to delete a resource can delete any resource. This attack appears to be exploitable via the user must be authorized. This vulnerability appears to have been fixed in 2.3.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1000011
- https://github.com/api-platform/core/issues/2364
- https://github.com/api-platform/core/pull/2441
- https://github.com/FriendsOfPHP/security-advisories/blob/master/api-platform/core/CVE-2019-1000011.yaml
