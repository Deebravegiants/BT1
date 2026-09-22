# [C] cruddl vulnerable to ArangoDB Query Language (AQL) injection through flexSearch

## Summary
Severity: Critical
Advisory: GHSA-qm4w-4995-vg7f
CVE: CVE-2022-36084
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-qm4w-4995-vg7f
Type: github-advisory

## Affected
- npm: `cruddl` — affected >=3.0.0 <3.0.2
- npm: `cruddl` — affected >=1.1.0 <2.7.0

## Details
### Impact

If a vunerable version of cruddl is used to generate a schema that uses `@flexSearchFulltext`, users of that schema may be able to inject arbitrary AQL queries that will be forwarded to and executed by ArangoDB.

Schemas that do not use `@flexSearchFulltext` are not affected.

The attacker needs to have `READ` permission to at least one root entity type that has `@flexSearchFulltext` enabled.

### Patches

The issue has been fixed in version 3.0.2 and in version 2.7.0 of cruddl.

### Workarounds

Users can temporarily remove `@flexSearchFulltext` from their schemas before they can update cruddl.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [cruddl](https://github.com/AEB-labs/cruddl)
* Email us at [security@aeb.com](mailto:security@aeb.com)

## References
- https://github.com/AEB-labs/cruddl/security/advisories/GHSA-qm4w-4995-vg7f
- https://nvd.nist.gov/vuln/detail/CVE-2022-36084
- https://github.com/AEB-labs/cruddl/pull/253
- https://github.com/AEB-labs/cruddl/commit/13b9233733ed6fc822718a07bc90a80cd3492698
- https://github.com/AEB-labs/cruddl
