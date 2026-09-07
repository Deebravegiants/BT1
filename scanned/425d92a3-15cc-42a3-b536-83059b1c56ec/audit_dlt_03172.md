# [M] Mitigation of M-11: Issue NOT mitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/65
Type: code-finding

## Details
## Mitigated issue
[M-11: Residual ETH unreachable and unuitilized in SafEth.sol](https://github.com/code-423n4/2023-03-asymmetry-findings/issues/152)

The issue was that the rounding losses from partitioning `msg.value` in `stake()` and `rebalanceToWeights()` was left irretrievably in the contract.

## Mitigation review
Previously `rebalanceToWeights()` withdrew all staked funds and redeposited only the ether that the contract received. Now, it redeposits its entire balance. As such, the rounding losses still remain in the contract after a call to `rebalanceToWeights()`, but the next time it is called this dust will be redeposited. Thus, at least `rebalanceToWeights()` doesn't gather dust (even though it's "not going to be used often, if at all").

The issue in `stake()` remains unmitigated per se. The dust generated there would of course also be picked up by `rebalanceToWeights()`, but since `rebalanceToWeights()` is "not going to be used often, if at all", and causes a significant loss for the protocol ([M-07](https://github.com/code-423n4/2023-03-asymmetry-findings/issues/765)), this issue cannot be considered mitigated.

## Suggestion
Sweep the dust in `stake()` instead by adding the balance to `msg.value`. Or use the entire balance in `unstake()`. These functions will be called frequently and it doesn't hurt to reward users with some dust.
Note that this would entail that [this check](https://github.com/asymmetryfinance/smart-contracts/blob/ec582149ae9733eed6b11089cd92ca72ee5425d6/contracts/SafEth/SafEth.sol#L148-L151) in `unstake()` would have to be removed:
```solidity
require(address(this).balance - ethBefore != 0, "Receive zero Ether");
```
See also the new issue titled "Reappearance of M-02 in SafEth.unstake()" for another reason this check should be removed.
