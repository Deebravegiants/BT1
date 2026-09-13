# [M] OpenCTI May Bypass Introspection Restriction

## Summary
Severity: Medium
Advisory: GHSA-4mvw-j8r9-xcgc
CVE: CVE-2024-37155
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-4mvw-j8r9-xcgc
Type: github-advisory

## Affected
- PyPI: `pycti` — affected >=0 <6.1.9

## Details
### Summary

The regex validation used to prevent Introspection queries can be bypassed by removing the extra whitespace, carriage return, and line feed characters from the query.

### Details

GraphQL Queries in OpenCTI can be validated using the `secureIntrospectionPlugin`.

### Impact
Bypassing this restriction allows the attacker to gather a wealth of information about the GraphQL endpoint functionality that can be used to perform actions and/or read data without authorization.  These queries can also be weaponized to conduct a Denial of Service (DoS) attack if sent repeatedly.

## References
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-4mvw-j8r9-xcgc
- https://nvd.nist.gov/vuln/detail/CVE-2024-37155
- https://github.com/OpenCTI-Platform/opencti/commit/f87d96918c63b0c3d3ebfbea6c789d48e2f56ad5
- https://github.com/OpenCTI-Platform/opencti
- https://github.com/OpenCTI-Platform/opencti/blob/6343b82b0b0a5d3ded3b30d08ce282328a556268/opencti-platform/opencti-graphql/src/graphql/graphql.js#L83-L94
- https://github.com/pypa/advisory-database/tree/main/vulns/pycti/PYSEC-2024-313.yaml
