# [H] AGV-1 | Mishandling Of Gas Stipends

## Summary
Severity: High
Contest weight: 0.5813
Dataset id: 20526
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol charges users an amount for gas since the protocol employs an asynchronous model where keepers pick the transactions up and execute them. The protocol checks whether the user has sent enough ETH in msg.value and if so adds their transaction to the uncompleted transaction queue.

The issue here comes in due to how those gas fees are handled. The following checks whether the user has sent enough funds to cover the gas to be expended by the keeper:
```solidity
require(msg.value >= gas, "AggregateVault: !gasRequirement");
```
The issue with the above check is that it assumes that gas is in terms of ETH instead of in gas units as it is.

Given that the gas stipend for a request is within the 100,000 - 1,000,000 range the transaction's gas cost on the user's side will be extremely low - less than a billionth of a cent since ETH is in 18 decimals. This will cause the protocol to lose funds in keeper gas fees on every deposit/withdrawal request that gets executed.

## Recommendation
Consider converting the gas units into a notional value before checking whether the amount passed by the user is sufficient by multiplying it by tx.gasprice.
