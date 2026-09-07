# [C] Relyra SAML SignatureValue not cryptographically verified -> authentication bypass

## Summary
Severity: Critical
Advisory: GHSA-jv46-xfwm-36j7
CVE: CVE-2026-49454
CWE: CWE-287, CWE-347
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-jv46-xfwm-36j7
Type: github-advisory

## Affected
- Hex: `relyra` — affected >=1.0.0 <1.2.0

## Details
## Summary

Relyra `1.0.0` and `1.1.0` accept forged SAML signatures because `SignatureValue` was not cryptographically verified before the library returned a successful authentication result.

## Details

In `1.0.0` and `1.1.0`, the XMLDSig trust boundary was incomplete. `:public_key.verify` over the exclusive-C14N canonicalized `SignedInfo` was not performed against the configured IdP certificate's public key, `DigestValue` was not recomputed over the canonicalized referenced element, and `canonicalize/2` remained an unused passthrough in the signature-verification path. The result was a structure-only acceptance path where document shape and trust-source rejection could succeed without proving the signature bytes.

## Impact

A forged `SignatureValue` carrying an attacker-controlled `NameID` can be accepted as `{:ok}`. Any relying-party application using Relyra `1.0.0` or `1.1.0` can be logged into as an arbitrary user if it trusts the affected response path.

## Patches

Relyra `1.2.0` closes the gap with real exclusive-C14N canonicalization, `:public_key.verify` against the configured IdP certificate's public key, and a constant-time `DigestValue` recompute/compare bound to the exact consumed node on both `verify/4` and `verify_metadata_root/4`.

## Workarounds

There is no safe configuration of `1.0.0` or `1.1.0`. Upgrade to `1.2.0` or later.

## Resources

- Fix commit `2e45689` (wire real XMLDSig crypto into the candidate arm)
- Fix commit `8910200` (close metadata trust bypass, pin over DER)
- Regression proof: `test/security/xml/adversarial_crypto_test.exs`, `test/relyra/metadata/auto_refresh_test.exs`, `test/security/ci_gate_integrity_test.exs`

## References
- https://github.com/szTheory/relyra/security/advisories/GHSA-jv46-xfwm-36j7
- https://nvd.nist.gov/vuln/detail/CVE-2026-49454
- https://github.com/szTheory/relyra/commit/2e456897af3158c175bb490ce7fc51d6241c8922
- https://github.com/szTheory/relyra/commit/8910200
- https://github.com/szTheory/relyra
