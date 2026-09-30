# [H] OpenAM Authentication Bypass via MSISDN LDAP Injection

## Summary
Severity: High
Advisory: GHSA-xq73-fvmr-jvmm
CVE: CVE-2026-46619
CWE: CWE-1188, CWE-90
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-xq73-fvmr-jvmm
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-auth-msisdn` — affected >=0 <16.1.1

## Details
## Summary

**Description**

An LDAP Injection (CWE-90) vulnerability in the MSISDN authentication module allows an unauthenticated, remote attacker to obtain an arbitrary OpenAM session without a password in the default trusted gateway configuration. This impacts OpenAM Community Edition through version 16.0.6. This issue was patched in version 16.1.1.

## Impact
OpenAM deployments through version 16.0.6 that have MSISDN enabled are potentially affected. This enables a pre-authentication login bypass for any realm where an MSISDN module instance is enabled in an authentication chain and reachable through the trusted-gateway list, which allows all traffic by default. The request-supplied MSISDN value was concatenated directly into an LDAP search filter. The resulting OpenAM session is a normal authenticated session for the matched user.

## Patch
This has been patched in OpenAM Community Edition version 16.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-xq73-fvmr-jvmm
- https://github.com/OpenIdentityPlatform/OpenAM
