# [H] H-08 MitigationConfirmed

## Summary
Severity: High
Chain: Smart contract
Component: 2023-08-pooltogether-mitigation
Published: 2023-08-23
Source: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/41
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-prize-pool/blob/main/src/PrizePool.sol#L340-L347
https://github.com/GenerationSoftware/pt-v5-prize-pool/blob/main/src/PrizePool.sol#L314-L318


# Vulnerability details

## Original Issue
[H-08 - Increasing reserves breaks PrizePool accounting](https://github.com/code-423n4/2023-07-pooltogether-findings/issues/147)

## Details
The previous implementation to increase reserves in the PrizePool contract didn't take into account the injected reserves, which caused the accounted balance in the prize pool to not be properly updated.
The original finding explains in detail how not updating correctly the accounted balance when increasing reserves allowed a vault to effectively steal the prize token contribution by double counting the initial injection into the reserves.

## Mitigation
The intention of the implemented mitigation is to keep track of all the injected reserves that happens when executing the [`contributeReserve()`](https://github.com/GenerationSoftware/pt-v5-prize-pool/blob/main/src/PrizePool.sol#L514-L519), to achieve this, a new variable is added, the `directlyContributedReserve`, which is updated each time a contribution is made.
```solidity
function contributeReserve(uint96 _amount) external {
  _reserve += _amount;
  //@audit-info => Keep track of all the injected contributions.
  directlyContributedReserve += _amount;
  prizeToken.safeTransferFrom(msg.sender, address(this), _amount);
  emit ContributedReserve(msg.sender, _amount);
}
```

- Also, this variable is now added when computing how many tokens have been accounted for by using the [`_accountedBalance()`](https://github.com/GenerationSoftware/pt-v5-prize-pool/blob/main/src/PrizePool.sol#L763-L766).
```solidity
function _accountedBalance() internal view returns (uint256) {
  Observation memory obs = DrawAccumulatorLib.newestObservation(totalAccumulator);
  //@audit-info => directlyContributedReserve is considered when computing the total amount of tokens that have been accounted
  return (obs.available + obs.disbursed) + directlyContributedReserve - _totalWithdrawn;
}
```

### Conclusion
- The mitigation successfully fixes the original issue about breaking the PrizePool accounting balances when increasing reserves

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/41_
