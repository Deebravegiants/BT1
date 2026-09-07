# [M] Prototype Pollution in Ajv

## Summary
Severity: Medium
Advisory: GHSA-v88g-cgmw-v5xw
CVE: CVE-2020-15366
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-v88g-cgmw-v5xw
Type: github-advisory

## Affected
- npm: `ajv` — affected >=0 <6.12.3

## Details
An issue was discovered in ajv.validate() in Ajv (aka Another JSON Schema Validator) 6.12.2. A carefully crafted JSON schema could be provided that allows execution of other code by prototype pollution. (While untrusted schemas are recommended against, the worst case of an untrusted schema should be a denial of service, not execution of code.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15366
- https://github.com/ajv-validator/ajv/commit/65b2f7d76b190ac63a0d4e9154c712d7aa37049f
- https://github.com/ajv-validator/ajv
- https://github.com/ajv-validator/ajv/releases/tag/v6.12.3
- https://github.com/ajv-validator/ajv/tags
- https://hackerone.com/bugs?subject=user&report_id=894259
- https://security.netapp.com/advisory/ntap-20240621-0007
