# [H] OpenAM Arbitrary OAuth Token Minting via Push Registration

## Summary
Severity: High
Advisory: GHSA-cj8f-2fhf-826r
CVE: CVE-2026-46498
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-cj8f-2fhf-826r
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-oauth2` — affected >=0 <16.1.1

## Details
## Summary

**Description**

An Authorization Bypass Through User-Controlled Key (CWE-639) exists in OpenAM's stateful OAuth2 token-read path. Under certain conditions, this may allow an attacker to forge OAuth2 bearer tokens and OIDC ID tokens with arbitrary subject, client, realm, and scope. This affects OpenAM Community Edition through version 16.0.6.

The OAuth2 token-read path reads caller-supplied token identifiers from the shared Core Token Store (CTS) without placing them in an OAuth-only namespace and without binding the row's trusted CTS type to the expected OAuth token family, so any CTS row whose BLOB claims to be an OAuth token is accepted on the read path with no integrity check.

## Impact

OpenAM Community Edition deployments through version 16.0.6 with the OAuth2 Provider service enabled in a realm are potentially affected, but the vulnerable read path is only reachable once an attacker can place attacker-controlled JSON into the shared CTS under an identifier they know. For example, an anonymous Push Notification SNS callback handler, reachable by any low-privileged user in a Push Notification-enabled realm after a single legitimate Push registration can trigger the exploit.

In any deployment where such a primitive exists, an attacker can forge OAuth2 bearer tokens with attacker-chosen userName, clientID, realm, and scope. The compromise does not by itself create an OpenAM SSO session or grant admin-console access.

## Patch

This has been patched in OpenAM Community Edition version 16.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-cj8f-2fhf-826r
- https://github.com/OpenIdentityPlatform/OpenAM
- https://github.com/OpenIdentityPlatform/OpenAM/releases/tag/16.1.1
