# [M] AIIR verification and policy gates could report success without enforcing the control (fail-open)

## Summary
Severity: Medium
Advisory: GHSA-73p9-6hrp-8qhr
CWE: CWE-347, CWE-636
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-73p9-6hrp-8qhr
Type: github-advisory

## Affected
- PyPI: `aiir` — affected >=0 <1.7.0

## Details
### Summary
Several of AIIR's verification and policy paths could return a success/"verified" result without actually enforcing the control they represent — they could **fail open** rather than fail closed. For a tool whose purpose is trustworthy verification, a consumer relying on these gates may have treated unverified or non-conforming input as verified.

Found during an internal adversarial hardening review of AIIR (not a third-party audit). All paths are fixed in **1.7.0**.

### Affected paths
- A `require_signing` policy gate could be satisfied by a forgeable/empty field, so an unsigned or forged-bundle receipt could pass a "signing required" check without a valid signature.
- A CI verification path could report `success` regardless of the underlying verification result.
- A release-verification gate could advertise policy limits it did not actually enforce.
- A signature-verification path could be silently skipped for certain input categories, exiting success without verifying.

### Impact
A consumer relying on these gates (e.g. `require_signing`, release/policy verification, or the CI check) to block unsigned, forged, or non-conforming receipts could have received a false "verified"/"pass". Exploitation requires reliance on the affected gate; it does not forge valid signatures, nor does it compromise content-addressing or correctly-signed receipts.

### Patches
Fixed in **1.7.0**. Every affected path now fails closed, each with a regression test. Upgrade to `aiir >= 1.7.0`.

### Workarounds
None for earlier versions other than upgrading. Full cryptographic Sigstore verification (`pip install aiir[sign]`, `--verify-signature` with `--signer-identity`/`--signer-issuer`) provides defense in depth.

### Scope note
This advisory covers code present in released versions (`< 1.7.0`). Separately, an unreleased agent-receipt feature had pre-release forgery findings fixed before it shipped — those were never in a released version and are out of scope.

## References
- https://github.com/invariant-systems-ai/aiir/security/advisories/GHSA-73p9-6hrp-8qhr
- https://github.com/invariant-systems-ai/aiir
