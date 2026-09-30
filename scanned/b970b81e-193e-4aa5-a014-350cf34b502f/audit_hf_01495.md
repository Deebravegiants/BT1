# [C] C-3 An unlimited claim

## Summary
Severity: Critical
Contest weight: 0.0591
Dataset id: 7937
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An unlimited claim vulnerability exists in the claim function of the FantiumClaimingV1 contract. The function is supposed to record that a user has already claimed a reward by updating a mapping that tracks claimed status. However, the code uses the equality operator (==) instead of the assignment operator (=) when attempting to update the mapping. As a result, the mapping is never changed, so the contract believes the user has not claimed yet on every call. Any address that holds a qualifying NFT can invoke the claim function repeatedly, each time passing the superficial check and receiving the full payout. This allows an attacker to drain all funds that the contract holds for rewards. The bug manifests when a holder calls the claim function; the contract transfers the reward, but the internal record remains unchanged, leading to an infinite loop of claims. Users expect to receive a single reward and see their balance reduced accordingly, but instead the contract continues to dispense funds, eventually leaving the contract balance at zero. The issue was discovered during a manual security audit by MixBytes, which identified the incorrect operator in the mapping update. The problem is hard to notice because the surrounding code appears to perform a guard check, and typical unit tests may only verify a single claim, not repeated calls. The vulnerability belongs to the class of logic errors where state is not correctly mutated, often referred to as missing state update or incorrect operator. To remediate, the equality operator must be replaced with an assignment so that the mapping is updated after a successful claim, and additional safeguards such as re‑entrancy protection and proper access controls should be considered. Until fixed, the contract can lose all reward funds, harming NFT holders and the overall protocol integrity.

## Recommendation
We recommend adding a change from == to =.
