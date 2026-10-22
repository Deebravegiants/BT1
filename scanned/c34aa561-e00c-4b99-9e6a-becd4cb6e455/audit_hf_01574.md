# [H] MJR-11 Incorrect minting

## Summary
Severity: High
Contest weight: 0.0114
Dataset id: 8464
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an incorrect minting bug that occurs when the protocol mints Diesel tokens based on the amount of USDT that a user is expected to transfer, without accounting for the transfer fee that USDT deducts in its transferFrom function. The root cause is the assumption that a fee‑on‑transfer token will move the full requested amount, leading the contract to calculate the mint amount from a value that does not match the actual balance increase. An attacker or any user can exploit this by initiating a mint operation with USDT; because USDT subtracts a fee, the contract receives less USDT than recorded, and consequently mints fewer Diesel tokens than the user paid for. The impact is that users receive a smaller token balance than expected, effectively losing value, and the protocol’s accounting invariants are broken because the total Diesel supply no longer reflects the true USDT collateral held. This condition manifests whenever the mint function is called with USDT, i.e., under normal usage of the protocol’s deposit‑and‑mint flow. The affected parties are users who mint Diesel with USDT and the protocol itself, which may suffer reputational damage and financial imbalance. The issue was discovered during a manual security audit that examined token transfer handling and identified that the USDT implementation charges a fee, a detail that was not reflected in the minting logic. The bug can be hard to notice because the UI may simply show a successful transaction, while the user’s Diesel balance is lower than anticipated, and the discrepancy may be attributed to market fluctuations rather than a contract error. To fix the problem, the contract should determine the actual amount of USDT received by measuring the balance before and after the transfer (balance difference) and use that precise value to calculate the number of Diesel tokens to mint, thereby eliminating reliance on the nominal transfer amount. This class of bug falls under fee‑on‑transfer token handling errors, where contracts fail to adjust for token‑level transfer fees, leading to incorrect accounting and token supply mismatches. From a user’s perspective the symptom is a missing or reduced Diesel balance after a successful USDT deposit, contrary to the expectation that the deposited amount translates one‑to‑one into newly minted tokens.

## Recommendation
We recommend to use balance difference to mint Diesel tokens.
