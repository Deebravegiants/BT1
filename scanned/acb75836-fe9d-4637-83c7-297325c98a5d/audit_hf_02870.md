# [H] Distribute is permissionless, allowing malicious users to specify 0 slippage and sandwich the swap

## Summary
Severity: High
Contest weight: 0.0508
Dataset id: 16145
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in a reward distribution function that can be called by any address without any access restriction. The function accepts a parameter that defines the minimum amount of output tokens expected from a swap, which is intended to protect against slippage. Because the function is permissionless, an attacker can invoke it and set this slippage parameter to zero, effectively disabling any safeguard against price movement. When the swap executes at an unfavorable rate, the attacker can sandwich the transaction – either by front‑running with a trade that moves the price before the distribution call and then back‑running after it – and capture the excess value that should have gone to legitimate reward recipients. This flaw occurs whenever the contract attempts to convert accrued rewards into another token via a decentralized exchange and relies on the caller‑provided slippage limit. Users who expect to receive a certain amount of reward tokens may instead receive nothing or a reduced amount, while the protocol’s reward pool can be drained or depleted. The issue was identified during a manual audit that examined function visibility and parameter validation. It is subtle because the function appears to perform a routine accounting operation, and a zero‑minimum output does not cause a revert, so the loss may only be observed as missing rewards after the fact. To remediate the problem, the contract should enforce an authorized keeper role for calling the distribution routine and should enforce a sensible minimum slippage threshold or use an on‑chain price oracle to validate the swap rate before execution. In essence, the bug is a classic case of missing access control combined with unchecked user‑controlled slippage, leading to potential fund loss and broken accounting guarantees.

## Recommendation
Set up a keeper role to distribute rewards.
