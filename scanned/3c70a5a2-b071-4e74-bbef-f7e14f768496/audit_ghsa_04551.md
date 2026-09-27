# [C] OpenAM: Pre-auth RCE via Java Deserialization in WebAuthn Authenticator Storage

## Summary
Severity: Critical
Advisory: GHSA-6c99-87fr-6q7r
CVE: CVE-2026-45051
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-24
Source: https://github.com/advisories/GHSA-6c99-87fr-6q7r
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-auth-webauthn` — affected >=0 <16.1.1

## Details
## Summary

**Description**

A deserialization of untrusted data vulnerability (CWE-502) exists in OpenAM's WebAuthn authentication module. Under certain conditions, this may allow an attacker to achieve arbitrary code execution in the context of the application server. This affects OpenAM Community Edition through version 16.0.6 and was patched in version 16.1.1.

This is not the default configuration. Exploitation requires that an attacker has previously been able to write attacker-controlled data to a storage attribute read by the WebAuthn module, and that the WebAuthn authentication flow is reachable.

## Impact
WebAuthn is a modern shipped module, but the vulnerable configuration requires either the default storage attribute to become attacker-writable, or the WebAuthn userAttribute to be set to an attacker-writable string attribute. That is not the default, but it is feasible in deployments because the product exposes the storage attribute as a free-form admin setting and does not warn or enforce that it must be server-managed and non-user-writable. This may exist through delegated administration, provisioning, write access to the backing LDAP/directory user record, legacy REST self-registration, or unsafe reconfiguration of `userAttribute`.

In any deployment where the attribute becomes user writable, an attacker can execute arbitrary code as the application server user. 

## Patch
This has been patched in OpenAM Community Edition version 16.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-6c99-87fr-6q7r
- https://github.com/OpenIdentityPlatform/OpenAM
