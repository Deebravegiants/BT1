# [M] Vault.register_deposit can revert when highest bid is bigger than deposit limit for asset in AlchemistV2

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L220
Type: audit-issue

## Details
# Vault.register_deposit can revert when highest bid is bigger than deposit limit for asset in AlchemistV2

## Summary
Vault.register_deposit can revert when highest bid is bigger than deposit limit for asset in AlchemistV2.
## Vulnerability Detail
After `AuctionHouse.settle`, the highest bid is then sent to `Vault.register_deposit` function. This function [will deposit](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L220) provided WETH amount into `AlchemistV2` contract.

`AlchemistV2._deposit` [doesn't allow to deposit more](https://github.com/alchemix-finance/v2-foundry/blob/master/src/AlchemistV2.sol#L1161-L1163) than `maximumExpectedValue` of asset. This limit is changing over the time when user deposit/withdraw from contract.
In such case tx will revert and project will not be funded. Admin will then need to refund highest bid and biffing can't continue as anyone can sent big amount in order to cause revert again.

Scenario.
1.AlchemistV2 contract has `maximumExpectedValue` for `ALCX_YVWETH` assets as 1_000_000.
2.Currently 910_000 `ALCX_YVWETH` already deposited to the contract.
3.AuctionHouse started auction for nft which ended with highest bid 100_000.
4.When calling settle function reverts as `maximumExpectedValue` limit is breached.
5.Admin needs to refund this bid, project didn't receive money, however it could get 90_000.
## Impact
Project doesn't receive funding
## Code Snippet
Provided above
## Tool used

Manual Review

## Recommendation
I believe that `Vault.register_deposit` should check how much it still can fund and in case if limit is less than highest bid, then deposit only allowed part and pay the rest to the bidder or leave that funds in the contract and deposit later, when limit will increase.
