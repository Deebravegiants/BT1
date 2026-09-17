# [H] Grackle has StackOverflowError in GraphQL query processing

## Summary
Severity: High
Advisory: GHSA-g56x-7j6w-g8r8
CVE: CVE-2023-50730
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-18
Source: https://github.com/advisories/GHSA-g56x-7j6w-g8r8
Type: github-advisory

## Affected
- Maven: `org.typelevel:grackle-core_2.13` — affected >=0 <0.18.0
- Maven: `org.typelevel:grackle-core_3` — affected >=0 <0.18.0
- Maven: `org.typelevel:grackle-core_sjs1_2.13` — affected >=0 <0.18.0
- Maven: `org.typelevel:grackle-core_sjs1_3` — affected >=0 <0.18.0
- Maven: `org.typelevel:grackle-core_native0.4_2.13` — affected >=0 <0.18.0
- Maven: `org.typelevel:grackle-core_native0.4_3` — affected >=0 <0.18.0
- Maven: `edu.gemini:gsp-graphql-core_2.13` — affected >=0
- Maven: `edu.gemini:gsp-graphql-core_3` — affected >=0
- Maven: `edu.gemini:gsp-graphql-core_sjs1_2.13` — affected >=0
- Maven: `edu.gemini:gsp-graphql-core_sjs1_3` — affected >=0
- Maven: `edu.gemini:gsp-graphql-core_native0.4_2.13` — affected >=0
- Maven: `edu.gemini:gsp-graphql-core_native0.4_3` — affected >=0

## Details
### Impact

Prior to this fix, the GraphQL query parsing was vulnerable to `StackOverflowError`s. The possibility of small queries resulting in stack overflow is a potential denial of service vulnerability.

This potentially affects all applications using Grackle which have untrusted users.

> [!CAUTION]  
> **No specific knowledge of an application's GraphQL schema would be required to construct a pathological query.**

### Patches
The stack overflow issues have been resolved in the v0.18.0 release of Grackle.

### Workarounds
Users could interpose a sanitizing layer in between untrusted input and Grackle query processing.

## References
- https://github.com/typelevel/grackle/security/advisories/GHSA-g56x-7j6w-g8r8
- https://nvd.nist.gov/vuln/detail/CVE-2023-50730
- https://github.com/typelevel/grackle/commit/56e244b91659cf385df590fc6c46695b6f36cbfd
- https://github.com/typelevel/grackle
- https://github.com/typelevel/grackle/releases/tag/v0.18.0
