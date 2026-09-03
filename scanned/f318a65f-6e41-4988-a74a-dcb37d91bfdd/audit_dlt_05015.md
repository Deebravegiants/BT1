# [M] An attacker  can give  weth to the contract and can send a little weth and cause  the else statement to get caused increasing the  seniorVaultWethRewards or deceasing and making it zero

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/50
Type: sherlock-finding

## Details
simon135

high

# An attacker  can give  weth to the contract and can send a little weth and cause  the else statement to get caused increasing the  seniorVaultWethRewards or deceasing and making it zero

## Summary
An attacker can send weth to the contract that can be small enough for the function to revert or be too much and not go into the right-if statement causing a loss of funds 
## Vulnerability Detail
2 scenarios:
1.
since the attacker transferred weth to the contract the harvest won't happen and the attacker can do this at every harvest call and make sure nobody gets the harvest.
or not hit the first if statement which balances glp through the batch contract which doesn't happen to cause glp to be not balanced causing liquidations to happen because glp is not balanced and if other tokens aren't doing well. Also, the assumption is broken because it's not evenly balanced.
2. There is not enough weth and if the protocol fee is more than the weth in the contract it will revert. So on the first few harvests, the function will revert which can cause the holders of the strategy not to get the harvest amount which then there Are no incentives to keep funds in.
## Impact
loss of funds and  loss of incentives for users
## Code Snippet
 ```solidity 
        // total weth harvested which is not compounded
        // its possible that this is accumulated value over multiple rebalance if in all of those it was below threshold
        uint256 wethHarvested = state.weth.balanceOf(address(this)) - state.protocolFee - state.seniorVaultWethRewards;

        if (wethHarvested > state.wethConversionThreshold) {
            // weth harvested > conversion threshold
            uint256 protocolFeeHarvested = (wethHarvested * state.feeBps) / MAX_BPS;
            // protocol fee incremented
            state.protocolFee += protocolFeeHarvested;

            // protocol fee to be kept in weth
            // remaining amount needs to be compounded
            uint256 wethToCompound = wethHarvested - protocolFeeHarvested;

            // share of the wethToCompound that belongs to senior tranche
            uint256 dnGmxSeniorVaultWethShare = state.dnGmxSeniorVault.getEthRewardsSplitRate().mulDivDown(
                wethToCompound,
                FeeSplitStrategy.RATE_PRECISION
            );
            // share of the wethToCompound that belongs to junior tranche
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/50_
