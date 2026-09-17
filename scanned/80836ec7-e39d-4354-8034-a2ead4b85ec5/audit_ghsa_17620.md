# [H] Janssen Config API returns results without scope verification

## Summary
Severity: High
Advisory: GHSA-373j-mhpf-84wg
CVE: CVE-2025-53003
CWE: CWE-200, CWE-269, CWE-284
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-30
Source: https://github.com/advisories/GHSA-373j-mhpf-84wg
Type: github-advisory

## Affected
- Maven: `io.jans:jans-config-api-server` — affected >=0 <1.8.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
The configAPI is an internal service and hence should never be exposed to the internet. With that said, this is a serious vulnerability that has a large internal surface attack area that exposes all sorts of information from the IDP including clients, users, scripts ..etc.

This affects all users of Janssen <1.8.0 and Gluu Flex <5.8.0

### Patches
_Has the problem been patched? What versions should users upgrade to?_
All users are advised to upgrade immediately to [1.8.0](https://github.com/JanssenProject/jans/releases/tag/v1.8.0) for Janssen users and [5.8.0](https://github.com/GluuFederation/flex/releases/tag/v5.8.0) For Flex users.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
The user can potentially fork and build the config api and patch it in their system following the commit here https://github.com/JanssenProject/jans/commit/92eea4d4637f1cae16ad2f07b2c16378ff3fc5f1

### References
_Are there any links users can visit to find out more?_
https://github.com/JanssenProject/jans/issues/11575
https://github.com/JanssenProject/jans/commit/92eea4d4637f1cae16ad2f07b2c16378ff3fc5f1

## References
- https://github.com/JanssenProject/jans/security/advisories/GHSA-373j-mhpf-84wg
- https://nvd.nist.gov/vuln/detail/CVE-2025-53003
- https://github.com/JanssenProject/jans/issues/11575
- https://github.com/JanssenProject/jans/commit/92eea4d4637f1cae16ad2f07b2c16378ff3fc5f1
- https://github.com/GluuFederation/flex/releases/tag/v5.8.0
- https://github.com/JanssenProject/jans
- https://github.com/JanssenProject/jans/releases/tag/v1.8.0
