# [C] C-1 Withdrawal of tokens from AMM

## Summary
Severity: Critical
Contest weight: 0.5470
Dataset id: 7126
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Controller allows to call AMM via callback:
withdrawsig = get_method_id("withdraw(address,uint256)") # AMM
controller.liquidate_extended(user, 0, frac, True,
market_amm.address, withdrawsig, [])
AMM.vy#L728
```solidity
def withdraw(user: address, frac: uint256) -> uint256[2]:
```
This method is sufficient to fulfill all the necessary conditions for a callback (Controller.vy#L525).
Using liquidate_extended, a hacker has the ability to withdraw any amount from AMM. It is also
possible to make a complete liquidation through a partial one.
The test script was handed over to the customer.

## Recommendation
It is recommended to use a specific signature for calling a callback.
