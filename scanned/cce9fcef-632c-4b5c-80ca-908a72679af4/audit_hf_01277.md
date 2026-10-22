# [M] Protect external facing LeverageManager functions from reentrancy

## Summary
Severity: Medium
Contest weight: 0.1483
Dataset id: 6027
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A number of the external functions in LeverageManager, namely deposit, withdraw, rebalance, and createNewLeverageToken read and change state, while doing external calls to user-specifiable contracts. This could result in exploits by temporarily affecting the contract's state through one of these functions initial calls and then re-entering into another to take advantage of this modified state.  
Some attacks have been considered with deposit and withdraw as the entrypoints, but utilizing reentrancy on them would likely not benefit an attacker. Others utilizing rebalance may allow a Leveraged Token to be put into a temporarily invalid state, where isStateAfterRebalanceValid would normally not pass, however, a reentrance would allow this invalid state to be utilized for minting shares at a discounted rate. Following the minting, the middle execution of rebalance can be cleaned up and it reset to a valid state to allow the transaction to confirm without reverting.

## Recommendation
Protect the noted functions with the nonReentrant modifier to disallow any potential for reentrancy and attacks it may yield. This should also be applied to any other external facing stateful functions.
