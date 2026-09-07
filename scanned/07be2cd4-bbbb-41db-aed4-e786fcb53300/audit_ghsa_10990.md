# [H] Ory Oathkeeper has an authentication bypass by cache key confusion

## Summary
Severity: High
Advisory: GHSA-4mq7-pvjg-xp2r
CVE: CVE-2026-33496
CWE: CWE-1289, CWE-305
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-4mq7-pvjg-xp2r
Type: github-advisory

## Affected
- Go: `github.com/ory/oathkeeper` — affected >=0 <0.40.10-0.20260320084801-198a2bc82a99

## Details
## Description

Ory Oathkeeper is vulnerable to authentication bypass due to cache key confusion. The `oauth2_introspection` authenticator cache does not distinguish tokens that were validated with different introspection URLs. An attacker can therefore legitimately use a token to prime the cache, and subsequently use the same token for rules that use a different introspection server.

## Preconditions

Ory Oathkeeper has to be configured with multiple `oauth2_introspection` authenticator servers, each accepting different tokens. The authenticators also must be [configured to use caching](https://www.ory.com/docs/oathkeeper/pipeline/authn#oauth2_introspection-configuration). An attacker has to have a way to gain a valid token for one of the configured introspection servers.

## Mitigation

Ory Oathkeeper now includes the introspection server URL in the cache key, preventing confusion of tokens.

Update to the patched version of Ory Oathkeeper. If that is not immediately possible, disable caching for `oauth2_introspection` authenticators.

## References
- https://github.com/ory/oathkeeper/security/advisories/GHSA-4mq7-pvjg-xp2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-33496
- https://github.com/ory/oathkeeper/commit/198a2bc82a99e0a77bd0ffe290cbdd5285a1b17c
- https://github.com/ory/oathkeeper
