# [H] ezplatform-graphql GraphQL queries can expose password hashes

## Summary
Severity: High
Advisory: GHSA-c7pc-pgf6-mfh5
CVE: CVE-2022-41876
CWE: CWE-200, CWE-922
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-c7pc-pgf6-mfh5
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-graphql` — affected >=1.0.0-rc1 <1.0.13
- Packagist: `ezsystems/ezplatform-graphql` — affected >=2.0.0-beta1 <2.3.12

## Details
### Impact
Unauthenticated GraphQL queries for user accounts can expose password hashes of users that have created or modified content, typically but not necessarily limited to administrators and editors.

### Patches

Resolving versions: Ibexa DXP v1.0.13, v2.3.12

### Workarounds
Remove the "passwordHash" entry from "src/bundle/Resources/config/graphql/User.types.yaml" in the GraphQL package, and other properties like hash type, email, login if you prefer.

### References

This issue was reported to us by Philippe Tranca ("trancap") of the company Lexfo. We are very grateful for their research, and responsible disclosure to us of this critical vulnerability. 

### For more information
If you have any questions or comments about this advisory, please contact Support via your service portal.

## References
- https://github.com/ezsystems/ezplatform-graphql/security/advisories/GHSA-c7pc-pgf6-mfh5
- https://nvd.nist.gov/vuln/detail/CVE-2022-41876
- https://developers.ibexa.co/security-advisories/ibexa-sa-2022-009-critical-vulnerabilities-in-graphql-role-assignment-ct-editing-and-drafts-tooltips
- https://github.com/ezsystems/ezplatform-graphql
