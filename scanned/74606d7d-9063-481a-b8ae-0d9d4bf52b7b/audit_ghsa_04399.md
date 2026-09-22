# [C] OpenAM Pre-auth User Profile Tampering via Anonymous SOAP Authn in Liberty IDPP/Discovery Endpoints

## Summary
Severity: Critical
Advisory: GHSA-p462-xxwx-pqf4
CVE: CVE-2026-45052
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-06-24
Source: https://github.com/advisories/GHSA-p462-xxwx-pqf4
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-federation-library` — affected >=0 <16.1.1

## Details
## Summary

**Description**

An Improper Authorization (CWE-285) issue in OpenAM's Liberty Web Services SOAP receiver allows an unauthenticated remote attacker to write persistent entries into the Liberty Discovery store on any user's LDAP entry, and into a shared root-realm Discovery branch. This impacts OpenAM Community Edition through version 16.0.6. This issue was patched in version 16.1.1.

Liberty ID-WSF is a legacy protocol superseded by SAML 2.0, OAuth, and OIDC, and deployments that intentionally leverage it assume the risks of an unmaintained federation stack. While Liberty is exposed in the shipped defaults, this bug does not require active Liberty consumers for the write itself. Downstream impact depends on whether anything consumes Discovery data. The endpoint accepts anonymous writes that are performed server-side by the Discovery handlers, bypassing the requester's LDAP and identity ACLs. The global Discovery path explicitly uses the internal admin token.

## Impact

OpenAM Community Edition deployments through version 16.0.6 that expose the Liberty Web Services component are potentially affected. An unauthenticated attacker who can reach the relevant endpoint may write persistent records to the discovery store, bypassing normal identity-layer access controls. 

These writes are performed with elevated internal privileges server-side.
In deployments that actively consume Liberty discovery data, manipulated records could influence service routing or security mechanism selection in subsequent requests. The severity of downstream impact varies by deployment..

## Patch
This has been patched in OpenAM Community Edition version 16.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-p462-xxwx-pqf4
- https://github.com/OpenIdentityPlatform/OpenAM
