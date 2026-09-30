# [H] Uncaught Panic in ORML Rewards Pallet

## Summary
Severity: High
Advisory: GHSA-5v93-9mqw-p9mh
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-14
Source: https://github.com/advisories/GHSA-5v93-9mqw-p9mh
Type: github-advisory

## Affected
- crates.io: `orml-rewards` — affected >=0 <1.2.1

## Details
## Summary
A vulnerability in the `add_share` function of the **Rewards** pallet (part of the ORML repository) can lead to an uncaught Rust panic when handling user-provided input exceeding the `u128` range.

## Affected Components
- **ORML Rewards** pallet (`rewards/src/lib.rs`)
- Any Substrate-based chain using ORML Rewards with `add_share` accepting unvalidated large `u128` inputs

## Technical Details
- `add_share` performs arithmetic on user-supplied values (`add_amount`) of type `T::Share` (mapped to `u128` in Acala).
- If `add_amount` is large enough (e.g., `i128::MAX`), the intermediate result may overflow and panic on the cast to `u128`.
- Validation occurs only after arithmetic, enabling a crafted input to trigger an overflow.

## Impact
A malicious user submitting a specially crafted extrinsic can cause a panic in the runtime:
- **Denial of Service** by crashing the node process.
- **Potential for invalid blocks** produced by validators.

## Likelihood
This issue is exploitable in production if there exists at least one rewards pool where reward tokens exceed twice the collateral tokens, allowing sufficiently large multiplication to exceed `u128` bounds.

## Remediation
- This issue is fixed in https://github.com/open-web3-stack/open-runtime-module-library/pull/1016

## Backport

The patch have been backported to following release branches:
- polkadot-stable2407
- polkadot-stable2409

A 1.0.1 patch release is made with this fix.

## References
- https://github.com/open-web3-stack/open-runtime-module-library/security/advisories/GHSA-5v93-9mqw-p9mh
- https://github.com/open-web3-stack/open-runtime-module-library/pull/1016
- https://github.com/open-web3-stack/open-runtime-module-library/commit/6720fcd92f44e5f204741b04fdef3b67b0fcf6bc
- https://github.com/open-web3-stack/open-runtime-module-library
