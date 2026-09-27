# [C] SAML authentication bypass due to missing validation on unsigned SAML messages

## Summary
Severity: Critical
Advisory: GHSA-hx5q-v6pj-533r
CWE: CWE-1395
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-26
Source: https://github.com/advisories/GHSA-hx5q-v6pj-533r
Type: github-advisory

## Affected
- Maven: `com.linecorp.centraldogma:centraldogma-server-auth-saml` — affected >=0 <0.64.3

## Details
### Impact

When SAML is used as the authentication mechanism, Central Dogma accepts unsigned SAML messages (assertions, logout requests, etc.) as they are, rather than rejecting them by default. As a result, an attacker can forge a SAML message to authenticate themselves, despite the fact that such an unsigned SAML message should be rejected.

### Patches

The vulnerability has been patched in Central Dogma 0.64.3 by updating its Armeria dependency to 1.27.2. All users who use SAML as the authentication mechanism must upgrade from 0.64.3 or later.

### Workarounds

A user can manually upgrade the `armeria-saml` module with the one from Armeria 1.27.2 or later, either by replacing the JAR in the Central Dogma distribution or by updating the dependency tree of the build.

### References

[`SamlMessageUtil.validateSignature()`](https://github.com/line/armeria/blob/0efc776988d71be4da6e506ec8a33c2b7b43f567/saml/src/main/java/com/linecorp/armeria/server/saml/SamlMessageUtil.java#L160-L163)

## References
- https://github.com/line/armeria/security/advisories/GHSA-4m6j-23p2-8c54
- https://github.com/line/centraldogma/security/advisories/GHSA-hx5q-v6pj-533r
- https://github.com/line/centraldogma/commit/16903426be2e954c050b3ee47b8c38ee3218f0eb
- https://github.com/line/centraldogma/commit/16903426be2e954c050b3ee47b8c38ee3218f0ebxz
- https://github.com/line/centraldogma
- https://github.com/line/centraldogma/releases/tag/centraldogma-0.64.3
