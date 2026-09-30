# [M] Unauthorized access to data in @sap-cloud-sdk/core

## Summary
Severity: Medium
Advisory: GHSA-gp2f-254m-rh32
CVE: CVE-2021-41251
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-gp2f-254m-rh32
Type: github-advisory

## Affected
- npm: `@sap-cloud-sdk/core` — affected >=0 <1.52.0

## Details
### Impact
This affects applications on SAP Business Technology Platform that use the SAP Cloud SDK and enabled caching of destinations.
In some cases, when user information was missing, destinations were cached without user information, allowing other users to retrieve the same destination with its permissions.
By default, destination caching is disabled. If it is enabled the maximum lifetime is 5 minutes which limits the attack vector.

### Patches
The problem was fixed by #1769 and #1770. The security for caching has been increased. The changes are released in version 1.52.0.

### Workarounds
Disable destination caching (it is disabled by default).

### References
[destination cache API docs](https://sap.github.io/cloud-sdk/api/1.51.0/modules/sap_cloud_sdk_core#destinationCache)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/SAP/cloud-sdk-js

## References
- https://github.com/SAP/cloud-sdk-js/security/advisories/GHSA-gp2f-254m-rh32
- https://nvd.nist.gov/vuln/detail/CVE-2021-41251
- https://github.com/SAP/cloud-sdk-js/pull/1769
- https://github.com/SAP/cloud-sdk-js/pull/1770
- https://github.com/SAP/cloud-sdk-js
