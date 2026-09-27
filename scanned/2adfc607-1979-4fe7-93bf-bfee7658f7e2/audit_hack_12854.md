# [H] Malicious executor of DCA orders can use a path with terrible price for the user and sandwich for profit

## Summary
Severity: High
Reporter: Lalanda
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165
Type: audit-issue

## Details
# Malicious executor of DCA orders can use a path with terrible price for the user and sandwich for profit

## Summary

Unstoppable:DEX allows users to create DCA orders (Dollar Cost Average). If enough time has passed a new DCA execution can be done, by anyone. Since the UniswapV3 path of the trade is defined by the executor of the trade, a malicious executor can define an unfavorable route for the user and sandwich the trade for profit.

## Vulnerability Detail

When creating the DCA order, for safety the user defines the twap interval to get the price from the uniswap pool and the max slippage the trades must have. The problem is that the DCA executor defines the UniswapV3 route to use for the trade and also for the twap price check.

Some pools already exist with extreme disparities from the market price. for example ETH/DAI with 0.01% fee has a price of 1632.5 DAI per ETH, while the market price on the other fee tiers is around 1961 DAI (04Jul2023 Mainnet). Or on Arbitrum WBTC/USDT on 0.3% fee tier has a price of 30680$ and on the fee tier of 0.05% has a price of 1524241978740483202618$.
For other pairs on certain fee tiers the pool does not exist at all, for example USDC/WBTC does not have a pool for 0.01% and 1% fee tiers (04Jul2023 Arbitrum).

An attack can look like this:

1. Bob creates a DCA order of 20.000 DAI to buy WETH 10 times in 2.000 USDT amounts for the following 10 weeks.
2. Eve sees that the price of WETH is 2000 DAI on the most liquid pool of 0.3% fee tier, but there is a pool with only dust amounts of liquidity in the 0.01% fee tier with a stale price of 3000 DAI per ETH. 
3. Eve funds the pool with 0.66 ETH on the tick of 3000 DAI price. In the same transaction Eve executes the DCA order of Bob using the path of the unbalanced pool. Eve then withdraws 2000 DAI from the liquidity pool. 
4. Bob gets 0.66 ETH for 2000 DAI, instead of 1 ETH for 33% loss. 

In step 2. another way Eve could have exploited Bob would be if there does not exist a pool in a certain fee tier. Eve can create the pool with only dust amounts of liquidity in the tick of the price she wants to use. Then Eve only needs to wait for the new pool to exist for longer than the twap interval set by Bob, for the DCA execution call to be successful.

## Impact

Unstoppable:DEX user of DCA orders can have some of their executions be done not at the market price. This can be used by a malicious executor to sandwich the user and profit from the difference in price.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L255-L268

## Tool used

Manual Review

## Recommendation

A few ways can be used to mitigate this problem.

1. DCA orders execution can only be done on pools and using routes that are whitelisted. A copy of SwapRouter.vy could be integrated with the DCA like the system used in the swaps made by the Vault.vy. 
2. Another option would be to use Chainlink oracle price feeds to assure that the amount out is between the slippage defined by the user.
3. The user when creating the DCA order defines the route to be used for the executions.
