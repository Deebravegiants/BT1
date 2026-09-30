# [H] OpenAM OAuth Client Impersonation via JWKS Resolver Cache

## Summary
Severity: High
Advisory: GHSA-f2cx-463q-7m2c
CVE: CVE-2026-47426
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-29
Source: https://github.com/advisories/GHSA-f2cx-463q-7m2c
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-oauth2` — affected >=0 <16.1.1

## Details
## Summary

**Description**

An Improper Authentication (CWE-287) issue in OpenAM's OAuth2 private_key_jwt client authentication path allows any registered OAuth2 client to mint tokens in the name of any other client whose key is published via a jwks_uri, without knowing the victim's signing key. This affects OpenAM Community Edition through version 16.0.6 and was patched in version 16.1.1.

## Impact

OpenAM Community Edition deployments through version 16.0.6 that have OAuth2 clients configured for private_key_jwt authentication with keys published via jwks_uri are potentially affected. An attacker holding any such client registration, their own, or one obtained through open dynamic client registration where enabled, can mint access tokens in any other such client's name, in any realm hosted by the OpenAM process.

## Patch
This has been patched in OpenAM Community Edition version 16.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-f2cx-463q-7m2c
- https://github.com/OpenIdentityPlatform/OpenAM
