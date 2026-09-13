# [M] AlchemistV2._checkMintingLimit can cause Vault.register_deposit to revert

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L220
Type: audit-issue

## Details
# AlchemistV2._checkMintingLimit can cause Vault.register_deposit to revert

## Summary
AlchemistV2._checkMintingLimit can cause Vault.register_deposit to revert
## Vulnerability Detail
After `AuctionHouse.settle` is called, the highest bid is then sent to `Vault.register_deposit` function. This function [will deposit](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L220) provided WETH amount into `AlchemistV2` contract and then [will borrow funds for receiver](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L230).
The amount that can be borrowed is calculated inside `_calculate_amount_to_mint` function.

`AlchemistV2._mint` function [calls `_checkMintingLimit` function](https://github.com/alchemix-finance/v2-foundry/blob/master/src/AlchemistV2.sol#L1221) in order to check if it's possible to mint amount that was asked by user.
https://github.com/alchemix-finance/v2-foundry/blob/master/src/AlchemistV2.sol#L1097-L1102
```solidity
    function _checkMintingLimit(uint256 amount) internal view {
        uint256 limit = _mintingLimiter.get();
        if (amount > limit) {
            revert MintingLimitExceeded(amount, limit);
        }
    }
```
In case if amount is bigger than limit, then tx will revert. This limit is changing over the time, it increases when users burn tokens and decreases when users mint them.
This limit is not checked when `_calculate_amount_to_mint` function is called.

Because of that function will revert when requested bigger amount, then limit.

Scenario.
1.AlchemistV2 contract currently has _mintingLimiter 45_000.
2.AuctionHouse started auction for nft which ended with highest bid 100_000.
3.It was deposited to the AlchemistV2 and amount to mint was calculated as 50_000(50% for simplicity).
4.When calling AlchemistV2.mint function reverts as _mintingLimiter limit is breached.
5.Admin needs to refund this bid, project didn't receive money, however it could mint 45_000.
## Impact
Project will not be funded.
## Code Snippet
Provided above
## Tool used

Manual Review

## Recommendation
Inside `_calculate_amount_to_mint` also check the mint limit.
