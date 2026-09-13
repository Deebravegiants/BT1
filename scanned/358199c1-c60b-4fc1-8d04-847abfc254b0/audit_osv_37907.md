# [C] Convoy: JWT Signature Verification Bypass Allows Authentication as Arbitrary Users

## Summary
Severity: Critical
Advisory: CVE-2026-33746
Aliases: GHSA-92pg-3w49-4w5x
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-33746
Type: osv

## Details
Convoy is a KVM server management panel for hosting businesses. From version 3.9.0-beta to before version 4.5.1, the JWTService::decode() method did not verify the cryptographic signature of JWT tokens. While the method configured a symmetric HMAC-SHA256 signer via lcobucci/jwt, it only validated time-based claims (exp, nbf, iat) using the StrictValidAt constraint. The SignedWith constraint was not included in the validation step. This means an attacker could forge or tamper with JWT token payloads — such as modifying the user_uuid claim — and the token would be accepted as valid, as long as the time-based claims were satisfied. This directly impacts the SSO authentication flow (LoginController::authorizeToken), allowing an attacker to authenticate as any user by crafting a token with an arbitrary user_uuid. This issue has been patched in version 4.5.1.

## References
- https://github.com/ConvoyPanel/panel/releases/tag/v4.5.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33746.json
- https://github.com/ConvoyPanel/panel/security/advisories/GHSA-92pg-3w49-4w5x
- https://nvd.nist.gov/vuln/detail/CVE-2026-33746
