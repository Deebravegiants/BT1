# [H] Valtimo backend libraries allows objects in the object-api to be accessed and modified by unauthorized users

## Summary
Severity: High
Advisory: GHSA-965r-9cg9-g42p
CVE: CVE-2025-48881
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-965r-9cg9-g42p
Type: github-advisory

## Affected
- Maven: `com.ritense.valtimo:objecten-api` — affected >=11.0.0.RELEASE
- Maven: `com.ritense.valtimo:object-management` — affected >=11.0.0.RELEASE
- Maven: `com.ritense.valtimo:object-management` — affected >=12.0.0.RELEASE <12.13.0.RELEASE
- Maven: `com.ritense.valtimo:objecten-api` — affected >=12.0.0.RELEASE <12.13.0.RELEASE

## Details
### Impact
All objects for which an object-management configuration exists can be listed, viewed, edited, created or deleted by unauthorised users.

If object-urls are exposed via other channels, the contents of these objects can be viewed independent of object-management configurations.

### Attack requirements
The following conditions have to be met in order to perform this attack:
- A user must be logged in
  - No relevant application roles are required
- At least one object-type must be configured via object-management
  - The scope of the attack is limited to objects that are configured via object-management.
  - The value of `showInDataMenu` is irrelevant for this attack

### Patches
This issue was patched in version 12.13.0.RELEASE.

### Workarounds
It is possible to override the endpoint security as defined in `ObjectenApiHttpSecurityConfigurer` and `ObjectManagementHttpSecurityConfigurer`. Depending on the implementation, this could result in loss of functionality.

## References
- https://github.com/valtimo-platform/valtimo-backend-libraries/security/advisories/GHSA-965r-9cg9-g42p
- https://nvd.nist.gov/vuln/detail/CVE-2025-48881
- https://github.com/valtimo-platform/valtimo-backend-libraries/commit/6ab04b30d3dab816bfea32d40ba50e5dd4517272
- https://github.com/valtimo-platform/valtimo-backend-libraries
