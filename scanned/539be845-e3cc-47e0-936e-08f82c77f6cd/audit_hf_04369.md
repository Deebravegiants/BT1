# [M] M-03 | Signatures in Valor can be reused

## Summary
Severity: Medium
Contest weight: 0.0450
Dataset id: 21575
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a replay‑type flaw in the Valor contract where the function that records daily USDC net fee revenue accepts a signed message from an address that holds the TREASURE_UPDATER_ROLE, but the contract does not keep any record of whether that signature has already been processed. Because there is no nonce, timestamp check, or replay‑prevention mechanism, the same cryptographic signature can be submitted an unlimited number of times. An attacker who possesses a valid signed payload – for example a report that claims a certain amount of USDC revenue – can call the function repeatedly, causing the contract to treat each submission as a fresh revenue event. This leads to the protocol’s accounting logic counting the same revenue multiple times, which may result in excess USDC being transferred to the treasury or to an attacker‑controlled address, depending on how the revenue distribution is implemented. The issue manifests whenever the TREASURE_UPDATER_ROLE or any address that can present a valid signature invokes the dailyUsdcNetFeeRevenue function; there is no condition that blocks subsequent calls with the same signature. Users of the protocol see inflated revenue figures, unexpected USDC balances, or refunds that do not match the actual activity. The flaw was discovered during a manual audit that examined the signature verification flow and noticed the absence of any replay protection. It can be hard to notice because the contract behaves correctly on the first submission, and the repeated calls may be spaced out or hidden among legitimate updates, making the over‑counting appear as normal revenue growth. Conceptually, the fix is to treat the signed message as a one‑time authorisation by adding a unique nonce (or a sequential identifier) to the signed data, storing a hash of used nonces, and rejecting any signature that references a nonce already marked as spent. This aligns the implementation with the standard replay‑attack mitigation pattern used for off‑chain signed authorisations and restores the integrity of the protocol’s accounting and fee distribution logic.

## Recommendation
Add a nonce to the signature, hash it and check if it's been already used.
