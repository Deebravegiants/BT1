# [H] OpenAM FreeMarker template injection

## Summary
Severity: High
Advisory: GHSA-7726-43hg-m23v
CVE: CVE-2024-41667
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-25
Source: https://github.com/advisories/GHSA-7726-43hg-m23v
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-oauth2` — affected >=0 <15.0.4

## Details
OpenAM is an open access management solution. In versions 15.0.3 and prior, the `getCustomLoginUrlTemplate` method in RealmOAuth2ProviderSettings.java is vulnerable to template injection due to its usage of user input. Although the developer intended to implement a custom URL for handling login to override the default PingOne Advanced Identity Cloud login page,they did not restrict the `CustomLoginUrlTemplate`, allowing it to be set freely. Commit fcb8432aa77d5b2e147624fe954cb150c568e0b8 introduces `TemplateClassResolver.SAFER_RESOLVER` to disable the resolution of commonly exploited classes in FreeMarker template injection. As of time of publication, this fix is expected to be part of version 15.0.4.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-7726-43hg-m23v
- https://nvd.nist.gov/vuln/detail/CVE-2024-41667
- https://github.com/OpenIdentityPlatform/OpenAM/commit/fcb8432aa77d5b2e147624fe954cb150c568e0b8
- https://github.com/OpenIdentityPlatform/OpenAM
