# [M] M-3 The Receive function revert

## Summary
Severity: Medium
Contest weight: 0.0320
Dataset id: 16019
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from the contract’s receive function, which is intended to reject plain Ether transfers when the protocol is configured to use an ERC‑20 token as its sole collateral. Because the receive function does not contain a conditional revert, any Ether sent to the contract – whether through a direct transfer, a self‑destruct, or a fallback call – is accepted even though the business logic assumes only ERC‑20 tokens will be held. This mismatch creates a situation where Ether can be deposited unintentionally and then become invisible to the contract’s accounting mechanisms, as the contract’s internal bookkeeping only tracks ERC‑20 balances. An attacker or an unwitting user can exploit the flaw by sending a small amount of Ether to the contract address; the transaction succeeds, but the Ether is not credited to any user balance and cannot be withdrawn through the existing functions. The impact is that funds may become permanently locked, the protocol’s invariant that collateral equals the declared ERC‑20 balance is broken, and users may experience symptoms such as “my transaction succeeded but my balance shows zero” or “the contract shows no Ether even though I sent some”. The issue manifests only when the collateral token is set to an ERC‑20 address; if the collateral were native Ether, the receive function would be appropriate. All parties that interact with the contract – token holders, liquidity providers, and the protocol itself – are affected because the hidden Ether distorts the overall asset pool. The problem was discovered during a manual audit that inspected the receive function and noted the absence of a revert condition for the ERC‑20 collateral mode. It can be hard to notice because the contract does not emit events on Ether receipt, the UI typically displays only ERC‑20 balances, and the receive function is silent, giving no immediate feedback. To remediate the issue, the contract should include an explicit check that reverts any incoming Ether when the collateral is an ERC‑20 token, for example by requiring msg.value == 0 or by disabling the receive/fallback functions entirely, thereby aligning the contract’s external behavior with its internal accounting assumptions.

## Recommendation
We recommend adding a check for the collateralERC20 address and the sender's address.
