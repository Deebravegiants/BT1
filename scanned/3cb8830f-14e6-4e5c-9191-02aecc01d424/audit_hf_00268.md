# [H] receiveCollateral

## Summary
Severity: High
Contest weight: 0.0998
Dataset id: 1370
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an access‑control weakness in the StabilityPool contract where the receiveCollateral() function can be invoked by any address, even though the documentation states that it should only be called by the ActivePool component. The root cause is the absence of a require statement or modifier that restricts msg.sender to the known ActivePool address. Because the function does not verify the caller, an attacker can submit arbitrary token addresses (_tokens) and amounts (_amounts) and cause the contract’s internal accounting to record these values as if they were genuine collateral deposits. Exploitation is straightforward: an adversary calls receiveCollateral() with chosen parameters, which updates the pool’s collateral balance mapping. This can be used to artificially inflate the pool’s apparent collateral, allowing the attacker to later claim a larger share of rewards or to trigger withdrawals that exceed the real assets held by the protocol. The impact is a breakdown of financial integrity – the StabilityPool may appear to hold more collateral than it actually does, leading to incorrect reward distribution, potential loss of user funds, and overall protocol instability. The condition under which the flaw manifests is any time after the contract is deployed, because the function is publicly accessible without any role checks. All participants who rely on the StabilityPool’s accounting – lenders, borrowers, and token holders – are affected, as the misreporting can cause their balances to be miscalculated or their withdrawals to fail. The issue was discovered during a security audit when reviewers compared the code against the contract comments and identified the missing access restriction. It can be difficult to notice in normal operation because the function does not emit distinct events that would raise alarms, and the comment alone does not enforce behavior, allowing the mismatch to go unnoticed until audited. To remediate, the contract should enforce that only the ActivePool address may invoke receiveCollateral(), typically by adding a require(msg.sender == activePool) check or applying an onlyActivePool modifier, and by emitting an event to log successful calls. As a class of bug, this is an "unrestricted external function" or "missing access control" vulnerability, which violates the business logic that only designated system components may modify core accounting state. From a user’s viewpoint, the symptom may be a sudden increase in reported collateral without having supplied any assets, or conversely a later failure to retrieve their expected rewards because the protocol’s internal balances are inconsistent. Users expect that only the protocol can adjust pool balances, but the reality is that any actor can manipulate those numbers, potentially causing funds to disappear or rewards to be misallocated.

## Recommendation
Allow only the ActivePool to call the receiveCollateral() function: require(msg.sender = address(active pool address), “Can only be called by ActivePool”)

@LilYeti: This was also caught by our official auditor, but good catch. 

Fixed this, #190, #285, already in code <https://github.com/code-423n4/2021-12-yetifinance/blob/main/packages/contracts/contracts/StabilityPool.sol#L1144>
