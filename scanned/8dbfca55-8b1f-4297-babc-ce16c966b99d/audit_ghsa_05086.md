# [M]  ZITADEL: Missing Token Audience Validation (`aud`) in JWT IdP Provider

## Summary
Severity: Medium
Advisory: GHSA-g5h5-m4hm-xjrr
CVE: CVE-2026-55669
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-g5h5-m4hm-xjrr
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=0 <1.80.0-v2.20.0.20260615132747-d184e976fc79

## Details
### Summary

An authentication bypass vulnerability was discovered in ZITADEL's external JWT Identity Provider (IdP) implementation.

When validating JSON Web Tokens (JWTs) from an external provider, ZITADEL properly checks the token's cryptographic signature and issuer (`iss`), but it fails to validate the audience (`aud`) claim.

As a result, any validly signed token from the trusted issuer will be accepted. An attacker who is a legitimate user of a completely separate service sharing the same enterprise Identity Provider can intercept or present their token for that service to ZITADEL, successfully authenticating as that user without authorization.

### Impact

In a controlled enterprise environment where Identity Providers are explicitly managed, the operational risk is localized. Exploitation requires that an attacker already possesses a valid standard user session token from a shared, trusted issuer intended for an entirely different relying party, limiting the vector to specific, rare cross-service setups where trust boundaries overlap.

### Affected Versions

Systems running one of the following versions are affected:

* **4.x**: `4.0.0` through `4.11.0` (including RC versions)
* **3.x**: `3.0.0` through `3.4.11` (including RC versions)

### Patches

The vulnerability has been addressed in the latest releases, where a required audience can be set in the IdP configuration. Once provided, audience validation will be enforced.

* **4.x**: Upgrade to $\ge$ [4.15.2](https://github.com/zitadel/zitadel/releases/tag/v4.15.2)
* **3.x**: Upgrade to $\ge$ [3.4.12](https://github.com/zitadel/zitadel/releases/tag/v3.4.12)

### Workarounds

The recommended solution is to update ZITADEL to a patched version.

If an immediate upgrade is not possible, you can mitigate the risk at the infrastructure layer:

1. **At the IdP:** Ensure the external Identity Provider issues scoped tokens with highly unique, non-overlapping audience values that cannot be misconstrued by separate service deployments.
2. **At the Perimeter:** Deploy a reverse proxy, API gateway, or Web Application Firewall (WAF) layer in front of ZITADEL to inspect incoming identity tokens and explicitly drop requests where the `aud` field does not strictly match ZITADEL's deployment target.

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

### Credits

Thanks to [Android-Login-Analysis](https://github.com/Android-Login-Analysis), Jason Zhou and [Pedro Giglioti](https://github.com/Punisher100) for reporting this vulnerability.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-g5h5-m4hm-xjrr
- https://github.com/zitadel/zitadel/commit/d184e976fc799a383bb6ef9f32c3bae11a3ef85f
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v3.4.12
- https://github.com/zitadel/zitadel/releases/tag/v4.15.2
