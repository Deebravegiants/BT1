# [H]  ZITADEL: Missing client_id binding in OIDC authorization code exchange and refresh token flows (RFC 6749 Section 4.1.3 violation)

## Summary
Severity: High
Advisory: GHSA-xqxv-4jc2-x56x
CVE: CVE-2026-55672
CWE: CWE-287, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-xqxv-4jc2-x56x
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=0 <1.80.0-v2.20.0.20260616131956-0973b074b488

## Details
### Summary

Zitadel's OAuth2 / OIDC `CodeExchange` and `RefreshToken` implementations omit a critical validation step to ensure that the requesting client matches the client that originally initiated the authorization flow. This violates RFC 6749 Section 4.1.3, which mandates that the authorization server must ensure the authorization code was issued to the authenticated confidential client.

### Impact

This flaw creates potential vulnerabilities in two main authentication phases, **provided specific external preconditions are met**:

* **Authorization Code Injection:** An attacker who intercepts an authorization code (via an independent application vulnerability such as XSS, referrer leakage, log access, or network interception) can exchange it using credentials from a completely different client (`ClientB`) registered on the same Zitadel instance. Zitadel will authenticate `ClientB` and issue tokens for the victim user without verifying the client binding.
* **Refresh Token Cross-Use:** An attacker who successfully steals a valid refresh token (via an external application exploit or data leak) can present it under a different client identity. Zitadel validates the token's format and expiration but fails to enforce client binding, allowing the attacker to maintain persistent access from an unauthorized client.
* Device Authorization Cross-Use: An attacker who intercepts or manipulates a device authorization flow grant can finalize the exchange using a different client context than the one that initiated the device session, bypassing intended client boundaries.

**Scope and Mitigation Factors:**

* **External Preconditions:** It is critical to note that exploiting either vector **requires a pre-existing vulnerability or data leak within the target application environment** to intercept the code or token in the first place. Securing the application layer against token theft remains outside the scope of Zitadel.
* **Multi-tenant risk:** On shared or multi-tenant instances, a client belonging to one tenant could theoretically exploit codes/tokens belonging to another tenant's clients if they are successfully intercepted.
* **PKCE protection:** Clients strictly using PKCE (Proof Key for Code Exchange) are partially mitigated against the authorization code injection vector, as the attacker would still require the `code_verifier`. However, PKCE does not protect against refresh token cross-use.

### Affected Versions

Systems running one of the following versions are affected:

* **4.x:** `4.0.0` through `4.15.1` (including RC versions)
* **3.x:** `3.0.0` through `3.4.11` (including RC versions)

### Patches

The vulnerability has been addressed in the latest releases by re-introducing strict client identity validation on the `CodeExchange` and `RefreshToken` grants.

Please upgrade to one of the following secure versions:

- **4.x**: Upgrade to $\ge$[4.15.2](https://github.com/zitadel/zitadel/releases/tag/v4.15.2)
- **3.x**: Update to $\ge$[3.4.12](https://github.com/zitadel/zitadel/releases/tag/v3.4.12)

### Workarounds

The recommended solution is to upgrade to a patched version.

To reduce exposure in the interim, ensure absolute adherence to application security best practices to prevent credential/token theft, enforce the use of **PKCE** for all clients to mitigate the Authorization Code Injection risk, and minimize refresh token lifespans.

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

### Credits

Thanks to [kodareef5](https://github.com/kodareef5), Shubham Raj / [Causal Security](https://causalsecurity.com/), and Gaurav Popalghat for identifying and responsibly reporting this or a part of this vulnerability.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-xqxv-4jc2-x56x
- https://nvd.nist.gov/vuln/detail/CVE-2026-55672
- https://github.com/zitadel/zitadel/commit/0973b074b48816757c47fe732b06d2488d3d284c
- https://github.com/zitadel/zitadel/commit/562403079a98cf2059cdac11865a45e2f285be71
- https://github.com/zitadel/zitadel/commit/5b1708e0e650398f0ebc3341714f0798b0118917
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v3.4.12
- https://github.com/zitadel/zitadel/releases/tag/v4.15.2
