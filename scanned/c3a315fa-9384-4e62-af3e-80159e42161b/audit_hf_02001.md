# [M] M-1 voluntaryExit shouldn't be public

## Summary
Severity: Medium
Contest weight: 0.0437
Dataset id: 11287
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an improper access‑control issue where the function voluntaryExit is declared public in contracts that are meant to be used only internally, such as the fee distribution contracts ElOnlyFeeDistributor and OracleFeeDistributor. Because the function is public, any external account or contract can invoke it, causing the contract to emit exit‑related events that off‑chain services monitor to determine when a validator has voluntarily left the system. The root cause is the mistaken visibility modifier; the developers intended the function to be internal, but it was left public, opening a path for unintended callers. An attacker can deploy a malicious contract or use a regular wallet to call voluntaryExit at arbitrary times, generating spurious exit events. Off‑chain services that rely on these events may interpret them as genuine validator exits, leading to incorrect accounting, premature reward distribution cessation, or even triggering slashing logic if the protocol assumes a real exit. The impact is therefore indirect but significant: users may see their rewards disappear, dashboards may show unexpected validator exits, and the protocol’s economic assumptions can be violated, potentially resulting in loss of fees or misallocation of funds. This condition can occur whenever any external entity interacts with the contract, especially if a client sends random or crafted transactions that invoke voluntaryExit. All participants that depend on the correctness of exit events – validators, delegators, fee recipients, and off‑chain monitoring tools – are affected. The issue was discovered during a formal audit by MixBytes, which flagged the visibility mismatch as a medium‑severity risk. Because the function does not revert or produce an on‑chain error when called, the problem can be hard to notice without reviewing the contract’s source or observing anomalous off‑chain behavior. The recommended remediation is to change the visibility of voluntaryExit from public to internal (or otherwise restrict it with proper access control), ensuring that only the contract’s own logic can trigger exit events and preventing external actors from fabricating them. This class of bug falls under improper function visibility or insufficient access control, which can lead to unintended state changes and break business logic that assumes only authorized components emit certain events.

## Recommendation
We recommend changing the function visibility to internal.
