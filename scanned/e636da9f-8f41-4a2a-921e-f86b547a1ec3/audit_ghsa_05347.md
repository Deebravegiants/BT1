# [M] OpenAM OAuth Authorization Bypass via PKCE Challenge

## Summary
Severity: Medium
Advisory: GHSA-4v2w-2wqp-mc85
CVE: CVE-2026-48717
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-29
Source: https://github.com/advisories/GHSA-4v2w-2wqp-mc85
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-oauth2` — affected >=0 <16.1.1

## Details
## Summary

**Description**

An Improper Authorization (CWE-285) issue in OpenAM's OAuth2 authorization-code grant allows a PKCE-protected authorization code to be redeemed without the required code_verifier. This affects OpenAM Community Edition through version 16.0.6 and was patched in version 16.1.1.

The authorize endpoint stores a code_challenge on the issued code, but the token endpoint only requires a code_verifier when the realm-wide codeVerifierEnforced setting is enabled, which ships disabled by default. With that setting off, the stored challenge is checked only if the caller supplies a verifier, so omitting the parameter skips PKCE verification entirely.

## Impact
OpenAM Community Edition deployments through version 16.0.6 using the default OAuth2 provider configuration are potentially affected. For public clients, an attacker who intercepts an authorization code can exchange it for tokens without knowing the verifier. For confidential clients, the attacker additionally needs client authentication material or an execution context that can redeem the code. A token request supplying an incorrect verifier is still rejected. The bypass is specifically the missing-parameter path.

## Patch
This has been patched in OpenAM Community Edition version 16.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-4v2w-2wqp-mc85
- https://github.com/OpenIdentityPlatform/OpenAM
