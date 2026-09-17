# [M] fhir-works-on-aws-authz-smart handles permissions improperly

## Summary
Severity: Medium
Advisory: GHSA-vv7x-7w4m-q72f
CVE: CVE-2022-39230
CWE: CWE-200, CWE-281
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-vv7x-7w4m-q72f
Type: github-advisory

## Affected
- npm: `fhir-works-on-aws-authz-smart` — affected >=3.1.1 <3.1.3

## Details
### Impact

This issue allows a client of the API to retrieve more information than the client’s OAuth scope permits when making “search-type” requests. This issue would not allow a client to retrieve information about individuals other than those the client was already authorized to access.

### Patches

We recommend that users of fhir-works-on-aws-authz-smart 3.1.1 or 3.1.2 upgrade to version 3.1.3 or higher immediately. Versions 3.1.0 and below are unaffected.

### Workarounds

There is no workaround for this issue. Please upgrade fhir-works-on-aws-authz-smart to version 3.1.3 or higher.

### References

https://github.com/awslabs/fhir-works-on-aws-deployment
https://github.com/awslabs/fhir-works-on-aws-authz-smart

### For more information

If you have any questions or comments about this advisory:

Email us at [fhir-works-on-aws-dev@amazon.com](mailto:fhir-works-on-aws-dev@amazon.com)

## References
- https://github.com/awslabs/fhir-works-on-aws-authz-smart/security/advisories/GHSA-vv7x-7w4m-q72f
- https://nvd.nist.gov/vuln/detail/CVE-2022-39230
- https://github.com/awslabs/fhir-works-on-aws-authz-smart/commit/203bbc0dd17de748c36b33c68b866ed2dfd613d3
- https://github.com/awslabs/fhir-works-on-aws-authz-smart
