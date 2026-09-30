# [H] Race condition in the Okta Java SDK

## Summary
Severity: High
Advisory: GHSA-j5gq-897m-2rff
CVE: CVE-2025-67505
CWE: CWE-362
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-j5gq-897m-2rff
Type: github-advisory

## Affected
- Maven: `com.okta.sdk:okta-sdk-root` — affected >=11.0.0 <20.0.1

## Details
### Description
In the Okta Java SDK, race conditions may arise from concurrent requests using the ApiClient class. This could cause a status code or response header from one request’s response to influence another request’s response.


### Affected product and versions
You may be affected if you meet the following preconditions:
- Using the Okta Java SDK between versions 11.0.0 and 20.0.0, and
- Implementing a multithreaded application with the ApiClient class where the response status code is used in access control flows

### Resolution
Upgrade Okta/okta-sdk-java to versions 21.0.0  or greater.

## References
- https://github.com/okta/okta-sdk-java/security/advisories/GHSA-j5gq-897m-2rff
- https://github.com/okta/okta-sdk-java/commit/abf4f128a0441f90cb7efcdcf4bde1aef8703243
- https://github.com/okta/okta-sdk-java
