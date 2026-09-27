# [H] OpenAPI Tools OpenAPI Generator uses HTTP in various files

## Summary
Severity: High
Advisory: GHSA-27j5-2h6r-c9q2
CVE: CVE-2019-11405
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-27j5-2h6r-c9q2
Type: github-advisory

## Affected
- Maven: `org.openapitools:openapi-generator` — affected >=0 <4.0.0-20190419.052012-560

## Details
OpenAPI Tools OpenAPI Generator before 4.0.0-20190419.052012-560 uses http:// URLs in various build.gradle, build.gradle.mustache, and build.sbt files, which may have caused insecurely resolved dependencies.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11405
- https://github.com/OpenAPITools/openapi-generator/issues/2253
- https://github.com/OpenAPITools/openapi-generator/pull/2248
- https://github.com/OpenAPITools/openapi-generator/pull/2697
- https://github.com/OpenAPITools/openapi-generator
