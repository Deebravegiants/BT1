# [H] OpenAPI Generator Online - Arbitrary File Read/Delete

## Summary
Severity: High
Advisory: GHSA-g3hr-p86p-593h
CVE: CVE-2024-35219
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-g3hr-p86p-593h
Type: github-advisory

## Affected
- Maven: `org.openapitools:openapi-generator-online` — affected >=0 <7.6.0

## Details
### Impact
Attackers can exploit the vulnerability to read and delete files and folders from an arbitrary, writable directory as anyone can set the output folder when submitting the request via the `outputFolder` option.

### Patches
The issue was fixed via https://github.com/OpenAPITools/openapi-generator/pull/18652 (included in v7.6.0 release)  by removing the usage of the `outputFolder` option.

### Workarounds
No workaround available.

### References
No other reference available.

## References
- https://github.com/OpenAPITools/openapi-generator/security/advisories/GHSA-g3hr-p86p-593h
- https://nvd.nist.gov/vuln/detail/CVE-2024-35219
- https://github.com/OpenAPITools/openapi-generator/pull/18652
- https://github.com/OpenAPITools/openapi-generator/commit/edbb021aadae47dcfe690313ce5119faf77f800d
- https://github.com/OpenAPITools/openapi-generator
