# [H] OpenAM Insecure SSO Cookie Initialization

## Summary
Severity: High
Advisory: GHSA-fpmh-vx4h-xc33
CVE: CVE-2026-53660
CWE: CWE-1004, CWE-1188, CWE-1275
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-14
Source: https://github.com/advisories/GHSA-fpmh-vx4h-xc33
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-core` — affected >=0 <16.1.1

## Details
## Summary

**Description**
An Insecure Default Initialization of Resource (CWE-1188) issue in the OpenAM default configuration ships the `iPlanetDirectoryPro` SSO cookie with `HttpOnly=false`. Also, the `iPlanetDirectoryPro` SSO cookie is used as a CSRF token in OAuth/OIDC flows. This affects OpenAM Community Edition through version 16.0.6 and was patched in version 16.1.1.

## Impact
A single click on an attacker link may yield full SSO session theft of any authenticated console user when chained with any other same-origin XSS in the OpenAM origin. The missing `SameSite` default also widens the CSRF surface. Also, because the consent flow reuses the SSO cookie as its CSRF token, any XSS in the OpenAM origin both steals the session and completes attacker-driven OAuth consent grants in one step.

## Patch
This has been patched in OpenAM Community Edition version 16.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-fpmh-vx4h-xc33
- https://github.com/OpenIdentityPlatform/OpenAM
- https://github.com/OpenIdentityPlatform/OpenAM/releases/tag/16.1.1
