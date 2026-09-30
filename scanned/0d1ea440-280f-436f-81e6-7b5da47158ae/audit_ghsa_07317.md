# [C] Apache Camel-Keycloak: The access-token validity window is not verified because the IS_ACTIVE check is missing from the TokenVerifier, allowing expired tokens to be accepted

## Summary
Severity: Critical
Advisory: GHSA-mqwc-6qwc-v9gq
CVE: CVE-2026-46455
CWE: CWE-613
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-mqwc-6qwc-v9gq
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-keycloak` — affected >=4.18.0 <4.18.3
- Maven: `org.apache.camel:camel-keycloak` — affected >=4.19.0 <4.21.0

## Details
Insufficient Session Expiration vulnerability in Apache Camel Keycloak Component.

The camel-keycloak security helper KeycloakSecurityHelper.parseAndVerifyAccessToken builds a Keycloak TokenVerifier using withChecks(...) with only the subject-exists check and the realm-URL (issuer) check. Keycloak's TokenVerifier.withChecks(...) appends to an initially empty check list - the upstream default checks are installed only when withDefaultChecks() is called - so the built-in IS_ACTIVE predicate, which validates the token's exp (expiration) and nbf (not-before) claims, is never applied. As a result the helper verifies the token signature, subject and issuer but does not enforce the token's validity window: an access token that is expired, or not yet valid, is accepted as valid. Routes that rely on this helper to authenticate inbound requests therefore accept access tokens that are outside their intended lifetime.
This issue affects Apache Camel: from 4.18.0 before 4.18.3, from 4.19.0 before 4.21.0.

Users are recommended to upgrade to version 4.21.0, which fixes the issue. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.3. The fix makes KeycloakSecurityHelper.parseAndVerifyAccessToken include the TokenVerifier.IS_ACTIVE check so that expired or not-yet-valid access tokens are rejected, aligning the helper with Keycloak's default check set. For deployments that cannot upgrade immediately, enforce token expiration outside the helper - for example validate the access token's exp/nbf claims in the route before trusting it, keep Keycloak access-token lifetimes short, and ensure any upstream gateway or resource server also validates the token validity window.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46455
- https://github.com/apache/camel/pull/23197
- https://github.com/apache/camel/pull/23204
- https://github.com/apache/camel/commit/39133b1ada37c60dea53f3b7db720dbd2ae73fa6
- https://github.com/apache/camel/commit/7f4c4736021aff4fad925eca3bf456b95db038f3
- https://camel.apache.org/security/CVE-2026-46455.html
- https://github.com/apache/camel
- https://github.com/apache/camel/releases/tag/camel-4.18.3
- https://github.com/apache/camel/releases/tag/camel-4.21.0
- https://issues.apache.org/jira/browse/CAMEL-23504
- http://www.openwall.com/lists/oss-security/2026/07/05/8
