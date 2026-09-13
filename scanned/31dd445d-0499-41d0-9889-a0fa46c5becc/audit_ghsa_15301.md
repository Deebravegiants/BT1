# [M] apollo-portal has potential unauthorized access issue

## Summary
Severity: Medium
Advisory: GHSA-c6c3-h4f7-3962
CVE: CVE-2024-43397
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-08-20
Source: https://github.com/advisories/GHSA-c6c3-h4f7-3962
Type: github-advisory

## Affected
- Maven: `com.ctrip.framework.apollo:apollo` — affected >=0 <2.3.0

## Details
### Impact
A vulnerability exists in the synchronization configuration feature that allows users to craft specific requests to bypass permission checks. This exploit enables them to modify a namespace without the necessary permissions.

### Patches
The issue was addressed with an input parameter check in #5192, which was released in version [2.3.0](https://github.com/apolloconfig/apollo/releases/tag/v2.3.0).

### Workarounds
To mitigate the issue without upgrading, follow the recommended practices to prevent Apollo from being exposed to the internet.

### Credits
The vulnerability was reported and reproduced by [Lakeswang](https://github.com/Lakes-bitgetsec).

### References
For any questions or comments regarding this advisory:
* Open an issue in [issue](https://github.com/apolloconfig/apollo/issues)
* Email us at [apollo-config@googlegroups.com](mailto:apollo-config@googlegroups.com)

## References
- https://github.com/apolloconfig/apollo/security/advisories/GHSA-c6c3-h4f7-3962
- https://nvd.nist.gov/vuln/detail/CVE-2024-43397
- https://github.com/apolloconfig/apollo/pull/5192
- https://github.com/apolloconfig/apollo/commit/f55b419145bf9d4f2f51dd4cd45108229e8d97ed
- https://github.com/apolloconfig/apollo
- https://github.com/apolloconfig/apollo/releases/tag/v2.3.0
