# [C] Discourse's WebAuthn challenge isn't cleared from user session after authentication

## Summary
Severity: Critical
Advisory: BIT-discourse-2025-53102
Aliases: CVE-2025-53102, GHSA-hv49-93h5-4wcv
Ecosystem: Bitnami
Published: 2025-07-31
Source: https://osv.dev/vulnerability/BIT-discourse-2025-53102
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.4.7

## Details
Discourse is an open-source community discussion platform. Prior to version 3.4.7 on the `stable` branch and version 3.5.0.beta.8 on the `tests-passed` branch, upon issuing a physical security key for 2FA, the server generates a WebAuthn challenge, which the client signs. The challenge is not cleared from the user’s session after authentication, potentially allowing reuse and increasing security risk. This is fixed in versions 3.4.7 and 3.5.0.beta.8.

## References
- https://github.com/discourse/discourse/commit/20bf65099bb861a141bc10e8a4eab65329d91802
- https://github.com/discourse/discourse/commit/8bc0cee2c00a514ea60f33ea6172da2ce5a05beb
- https://github.com/discourse/discourse/security/advisories/GHSA-hv49-93h5-4wcv
- https://nvd.nist.gov/vuln/detail/CVE-2025-53102
