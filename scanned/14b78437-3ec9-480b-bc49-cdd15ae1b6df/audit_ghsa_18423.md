# [M] Parse Server exposes the data schema via GraphQL API

## Summary
Severity: Medium
Advisory: GHSA-48q3-prgv-gm4w
CVE: CVE-2025-53364
CWE: CWE-497
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-10
Source: https://github.com/advisories/GHSA-48q3-prgv-gm4w
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=8.0.0 <8.2.2
- npm: `parse-server` — affected >=5.3.0 <7.5.3

## Details
### Impact

The Parse Server GraphQL API previously allowed public access to the GraphQL schema without requiring a session token or the master key. While schema introspection reveals only metadata and not actual data, this metadata can still expand the potential attack surface.

### Patches

The issue has been addressed by requiring the master key for schema introspection. Additionally, a new Parse Server configuration option, `graphQLPublicIntrospection`, has been introduced. This option allows developers to re-enable public schema introspection if their application relies on it. However, it is strongly recommended to use this option only temporarily and to update the application to function without depending on public introspection.

### Workarounds

None available.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-48q3-prgv-gm4w
- Fix for Parse Server 7: https://github.com/parse-community/parse-server/pull/9820
- Fix for Parse Server 8: https://github.com/parse-community/parse-server/pull/9819

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-48q3-prgv-gm4w
- https://nvd.nist.gov/vuln/detail/CVE-2025-53364
- https://github.com/parse-community/parse-server/pull/9819
- https://github.com/parse-community/parse-server/pull/9820
- https://github.com/parse-community/parse-server
