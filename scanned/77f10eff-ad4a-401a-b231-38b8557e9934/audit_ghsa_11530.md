# [H] Parse Server: Classes `_GraphQLConfig` and `_Audience` master key bypass via generic class routes

## Summary
Severity: High
Advisory: GHSA-7xg7-rqf6-pw6c
CVE: CVE-2026-31800
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-7xg7-rqf6-pw6c
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.5.2-alpha.12
- npm: `parse-server` — affected >=0 <8.6.25

## Details
### Impact

The `_GraphQLConfig` and `_Audience` internal classes can be read, modified, and deleted via the generic `/classes/_GraphQLConfig` and `/classes/_Audience` REST API routes without master key authentication. This bypasses the master key enforcement that exists on the dedicated `/graphql-config` and `/push_audiences` endpoints. An attacker can read, modify and delete GraphQL configuration and push audience data.

### Patches

The fix adds the affected internal classes to the `classesWithMasterOnlyAccess` list, ensuring that the generic `/classes/` routes enforce master key access consistently with the dedicated endpoints.

### Workarounds

There is no known workaround.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-7xg7-rqf6-pw6c
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.12
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.25

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-7xg7-rqf6-pw6c
- https://nvd.nist.gov/vuln/detail/CVE-2026-31800
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.25
- https://github.com/parse-community/parse-server/releases/tag/9.5.2-alpha.12
