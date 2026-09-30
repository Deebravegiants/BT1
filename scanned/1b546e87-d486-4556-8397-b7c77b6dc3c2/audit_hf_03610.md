# [M] `SurplusGuildMinter.getReward

## Summary
Severity: Medium
Contest weight: 0.7966
Dataset id: 19622
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `SurplusGuildMinter.getReward()` function [invokes](https://github.com/code-423n4/2023-12-ethereumcreditguild/blob/main/src/loan/SurplusGuildMinter.sol#L239) `ProfitManager.claimRewards()` that in a loop claims reward through all gauges/terms for `SurplusGuildMinter` as follows.
```solidity
function claimRewards(
    address user
) external returns (uint256 creditEarned) {
    address[] memory gauges = GuildToken(guild).userGauges(user);
    for (uint256 i = 0; i < gauges.length; ) {
        creditEarned += claimGaugeRewards(user, gauges[i]);
        unchecked {
            ++i;
        }
    }
}
```
Whereas `SurplusGuildMinter` works with all gauges, and there is no upper limit for the [`GuildToken.setMaxGauges(max)`](https://github.com/code-423n4/2023-12-ethereumcreditguild/blob/main/src/tokens/ERC20Gauges.sol#L444), the length of loop could be unbounded.

Each call to `stake()`, `unstake()`, or `getReward()` of `SurplusGuildMinter` will either consume excessive amount of gas, or revert with Out-Of-Gas reason after certain number of gauges/terms were added.

## Proof of Concept
1. Alice stakes **Credit** tokens in `SurplusGuildMinter`.
2. Some number of terms are added to the protocol.
3. When further Alice tries to call `stake()`, `unstake()`, or `getReward()`, the call reverts due to Out-Of-Gas reason:
```solidity
// Put inside test/unit/loan/SurplusGuildMinter.t.sol
function test_dos() public {
    address alice = address(789);

    // Number of terms that triggers OOG for stake/unstake/getReward
    uint256 numTerms = 6500;
    address[] memory terms = new address[](numTerms);

    guild.setMaxGauges(numTerms + 1);

    credit.mint(alice, 10e18);

    // Alice stakes Credit tokens
    vm.startPrank(alice);
    credit.approve(address(sgm), 10e18);
    sgm.stake(term, 10e18);
    vm.stopPrank();

    // Create terms
    credit.mint(address(this), 10e18 * numTerms);
    credit.approve(address(sgm), 10e18 * numTerms);
    for (uint256 i; i < numTerms; i++) {
        address _term = address(new MockLendingTerm(address(core)));
        terms[i] = _term;
        guild.addGauge(1, _term); // gaugeType = 1
        sgm.stake(_term, 10e18);
    }

    uint256 gasBefore =  gasleft();

    // Alice tries to call getRewards()
    sgm.getRewards(alice, term);

    uint256 gasAfter =  gasleft();

    uint256 BLOCK_GAS_LIMIT = 30e6;
    
    // getRewards() consumes more gas than block gas limit of 30Mil
    // reverts with OOG
    require(gasBefore - gasAfter > BLOCK_GAS_LIMIT);
}
```
Run Poc with the following command: `forge test --mp test/unit/loan/SurplusGuildMinter.t.sol --mt test_dos`

## Recommendation
Inside `SurplusGuildMinter.getReward(user, term)` call:
```solidity
ProfitManager(profitManager).claimRewards(address(this), term)
```
Instead of:
```solidity
ProfitManager(profitManager).claimRewards(address(this))
```
Since the purpose of `SurplusGuildMinter.getReward(user, term)` is to update the profit index only for a specific `term`, so there is no need to update profit indexes across all available terms.
