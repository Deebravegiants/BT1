# [M] The assumption that operator == to

## Summary
Severity: Medium
Contest weight: 0.2427
Dataset id: 497
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract uses `_msgSender()` to denote an operator who is operating on behalf of the user. This is typically used for meta-transactions where the operator is an intermediary/relayer who may facilitate gas-less transactions on behalf of the user. They may be the same address but it is safer to assume that they may not be.

While the code handles this separation of role in most cases, it misses doing so in `timelockDepositTo()` function where it accounts the `_timelockBalances` to the operator address instead of the user specified `to` address. It assumes they are the same. The corresponding usage in `_mintTimelock()` which is called from `withdrawWithTimelockFrom()` uses the user specified ‘from’ address and not the `_msgSender()`. Therefore the corresponding usage in `timelockDepositTo()` should be the same.

In the scenario where the operator address != user specified from/to addresses, i.e. meta-transactions, the timelock deposits and withdrawals are made to/from different addresses and so the deposits of timelocked tokens will fail because the operator’s address does not have the required amount of `_timelockBalances`.

Recommend changing `operator` to `from` on [L281](https://github.com/code-423n4/2021-06-pooltogether/blob/85f8d044e7e46b7a3c64465dcd5dffa9d70e4a3e/contracts/PrizePool.sol#L281) of `timelockDepositTo()` and specifying the scenarios where the role of the operator is applicable and document/implement those accordingly.

In the function `timelockDepositTo()` the msg.sender is using their timelocked funds to re-enter the pool. They can only spend their own funds; they should not be able to spend other user’s funds.

The warden is saying the `timelockDepositTo` should be callable by anyone and allow them to transfer other user’s funds from the timelock back into tickets. This actually introduces an attack vector.

I think sponsor is misunderstanding warden’s concern here. The issue is not that `msg.sender` is being checked, but that `_msgSender` is being checked. Happy to discuss this more if sponsor still disagrees, but I think the concern raised is valid.

## Recommendation
No recommendation
