# [H] OpenAM Authenticated Privilege Escalation via Raw Token Disclosure Session RPC

## Summary
Severity: High
Advisory: GHSA-vvhj-w2jq-263q
CVE: CVE-2026-45048
CWE: CWE-200, CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-vvhj-w2jq-263q
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-core` — affected >=0 <16.1.1

## Details
## Summary

Description

An insufficient authorization (CWE-285) and information exposure (CWE-200) issue in OpenAM's session management endpoint allows a low-privileged authenticated user to retrieve active session credentials belonging to other users, including those with higher privileges. This affects OpenAM Community Edition through version 16.0.6 and was patched in version 16.1.1.

This may be related to CVE-2021-4201, a similar issue patched in ForgeRock Access Management, a separate product sharing a common codebase ancestry.

## Impact

OpenAM Community Edition deployments through version 16.0.6 using stateful session storage and exposing the session management endpoint are potentially affected. The endpoint does not enforce ownership or privilege checks when querying session information, meaning an authenticated user may retrieve active session credentials for arbitrary users. Successful exploitation requires a valid low-privilege session and knowledge of a target user's identity identifier, which may be obtainable through normal platform functionality.

If credentials belonging to a highly privileged account are obtained, this could enable further administrative actions within the platform

## Patch

This has been patched in OpenAM Community Edition version 16.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-vvhj-w2jq-263q
- https://github.com/OpenIdentityPlatform/OpenAM
