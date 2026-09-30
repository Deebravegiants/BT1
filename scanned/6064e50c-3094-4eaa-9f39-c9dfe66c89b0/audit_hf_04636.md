# [H] H-01 | Missing onlyLive Modifier

## Summary
Severity: High
Contest weight: 0.0522
Dataset id: 22375
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a missing access‑control check on the purchaseWithUSDC function, which should be restricted to the contract’s active state but is not protected by the onlyLive modifier. The root cause is a logical omission: the developer added the onlyLive guard to most sale functions but forgot to apply it to the USDC‑based purchase path. Because the contract can be put into a disabled or paused state, any function that lacks the onlyLive check will continue to execute even after the protocol intends to stop sales. An attacker or any user can therefore call purchaseWithUSDC after the contract has been disabled, causing the contract to mint new tokens and accept USDC payments when it should reject them. This exploitation is straightforward: the attacker observes that the contract’s pause flag is set, then invokes purchaseWithUSDC with a valid USDC amount; the function proceeds to mint tokens and transfer them to the caller, bypassing the intended sales shutdown. The impact includes unintended inflation of the token supply, loss of revenue for the protocol because sales continue when they should be halted, and erosion of trust as users may receive tokens in a state where the protocol claims sales are closed. The condition under which the bug manifests is any time the contract’s live flag is false (i.e., the contract is disabled) while the purchaseWithUSDC function remains callable. All participants who rely on the contract’s pause mechanism—such as token holders, investors, and the protocol team—are affected because the business rule that sales stop is violated. The issue was discovered during a manual security audit that compared the modifiers applied to each entry point and noticed the inconsistency. It can be hard to notice in testing because the function works correctly while the contract is live, and the missing guard only becomes apparent when the contract is paused, a state that may not be exercised in routine unit tests. To remediate, the purchaseWithUSDC function should be annotated with the onlyLive modifier (or an equivalent check of the contract’s live flag) so that any call while the contract is disabled reverts, restoring the intended sales shutdown behavior. In generic terms, this is an authorization or state‑validation bug where a privileged operation is not correctly gated by the contract’s lifecycle state, leading to a breach of accounting assumptions and allowing funds to be transferred or tokens to be minted when they should not be.

## Recommendation
Add an onlyLive modifier to the purchaseWithUSDC function.
