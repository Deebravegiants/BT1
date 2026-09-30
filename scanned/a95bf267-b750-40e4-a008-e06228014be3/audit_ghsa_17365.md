# [M] Improper Memory Cleanup in the Okta Java SDK

## Summary
Severity: Medium
Advisory: GHSA-qhr6-6cgv-6638
CVE: CVE-2025-66033
CWE: CWE-401
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-qhr6-6cgv-6638
Type: github-advisory

## Affected
- Maven: `com.okta.sdk:okta-sdk-root` — affected >=21.0.0 <24.0.1

## Details
### Description
In the Okta Java SDK, specific multithreaded implementations may encounter memory issues as threads are not properly cleaned up after requests are completed. Over time, this can degrade performance and availability in long-running applications and may result in a denial-of-service condition under sustained load.

### Affected product and versions
You may be affected by this vulnerability if you meet the following preconditions:
- Using the Okta Java SDK between versions 21.0.0 and 24.0.0, and
- Implementing a long-running application using the ApiClient in a multi-threaded manner.

### Resolution
Upgrade Okta/okta-sdk-java to versions 24.0.1 or greater. 

### Acknowledgement
Okta would like to thank Andrew Pikler (pyckle) for their discovery and responsible disclosure.

## References
- https://github.com/okta/okta-sdk-java/security/advisories/GHSA-qhr6-6cgv-6638
- https://nvd.nist.gov/vuln/detail/CVE-2025-66033
- https://github.com/okta/okta-sdk-java/commit/1daa9229a70fc38fb252aeaa637f82d0b0729b3f
- https://github.com/okta/okta-sdk-java
