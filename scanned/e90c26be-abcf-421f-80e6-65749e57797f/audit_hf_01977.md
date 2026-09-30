# [M] updatePair() is missing the pairOk() modifier

## Summary
Severity: Medium
Contest weight: 0.0159
Dataset id: 11139
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the function that updates a trading pair’s configuration. The function performs the state change but does not invoke the pairOk validation routine that is intended to enforce invariant checks on the new parameters. Because the modifier is omitted, the contract accepts any values supplied by the caller, including ones that violate business rules such as price bounds, fee limits, or token address validity. An attacker or a careless admin can therefore set malformed or malicious attributes, causing the pair to behave incorrectly – for example, returning extreme prices, rejecting legitimate trades, or allowing trades at a rate that drains liquidity. The impact is that users may see unexpected zero balances, failed swaps, or loss of funds when interacting with the affected pair. The flaw manifests whenever updatePair is called, which can be triggered by any account that possesses the update permission; the missing check means the contract does not guard against out‑of‑range or contradictory values. The issue was uncovered during a systematic audit that compared the function signature against the expected security modifiers and noticed the absence of pairOk. It can be hard to notice because the function executes without reverting and the contract does not emit an explicit warning, so the state appears to change normally while the hidden invariants are silently broken. The appropriate remediation is to attach the pairOk modifier (or an equivalent internal validation call) to the updatePair function so that every new configuration is verified against the protocol’s rules before being persisted. In generic terms this is an input‑validation omission that belongs to the class of unchecked state‑update bugs, where missing constraints allow arbitrary data to corrupt critical accounting logic. From a user’s perspective the symptom may be a trade that returns zero output, a pair that shows absurd price quotes, or a balance that appears to disappear after an update, contrary to the expectation that updating a pair only changes metadata without affecting asset safety.

## Recommendation
Add the pairOk() modifier to updatePair().
