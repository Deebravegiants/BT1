# [H] OpenAM Account Takeover via Unverified Password Change in OAuth2 Module

## Summary
Severity: High
Advisory: GHSA-gf57-4mp6-m85x
CVE: CVE-2026-46623
CWE: CWE-1391, CWE-620
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-gf57-4mp6-m85x
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-auth-oauth2` — affected >=0 <16.1.1

## Details
## Summary

**Description**

An Unverified Password Change (CWE-620) and Use of Weak Credentials (CWE-1391) issue in OpenAM's OAuth2 authentication module silently rewrites a local user's password to the literal string of their username on OAuth2 re-login of an existing account. The default ldapService chain then accepts the username as the password for that user, allowing an unauthenticated attacker to obtain a session via the standard authenticate endpoint with both username and password set to the username, without any IdP interaction. This affects OpenAM Community Edition through version 16.0.6 and was patched in version 16.1.1.

## Impact
OpenAM Community Edition deployments through version 16.0.6 that use the OAuth2 authentication module with account creation enabled (the default) are potentially affected. After two OAuth logins of a given user, that user's local password becomes their username, and the account is reachable through the default ldapService chain with username as both identifier and password. For pre-existing users whose IdP profile resolves against an existing local identifier, the rewrite fires on the very first re-login.

Usernames shorter than the default minimum password length have the rewrite silently denied (so very short administrative accounts are not affected), and the same update path marks accounts active on every OAuth login, silently reactivating disabled accounts. 

Successful exploitation grants an unauthenticated attacker a session carrying the victim principal's privileges.

## Patch
This has been patched in OpenAM Community Edition version 16.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-gf57-4mp6-m85x
- https://github.com/OpenIdentityPlatform/OpenAM
