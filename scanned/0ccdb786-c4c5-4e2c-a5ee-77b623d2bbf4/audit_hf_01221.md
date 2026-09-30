# [M] maxSlippage is insufficient swap protection for unbalanced Curve Pools

## Summary
Severity: Medium
Contest weight: 0.2657
Dataset id: 5472
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently the Curve swap function utilizes a maxSlippage protection. This value is set by the DEFAULT_ADMIN_ROLE to a percentage (i.e. 0.98e18 or 1.02e18). It is then used as a check against the RELAYER during the swap to ensure the RELAYER specifies an acceptable minAmount parameter when doing the swap. It always specifies that the minAmount parameter must be amountIn * rates[inputIndex] / rates[outputIndex] * maxSlippage so with 1:1 priced tokens and max slippage set to 98% the minAmount would have to be 98 or greater when amountIn = 100. If all the same conditions existed, but max slippage was 102%, the minAmount would have to be 102.
Essentially maxSlippage provides a floor to ensure that the RELAYER is not making trades that incur more slippage than is acceptable.
Curve uses slippage to punish/reward making the Pool less/more healthy. So a trade that significantly moves the pool away from equilibrium will incur more slippage than one that does not substantively affect the equilibrium. If the pool is already imbalanced between the tokens, then trades that move it towards equilibrium will be rewards. This is done to encourage arbitragers to keep the stable pools in balance.
This graph helps us visualize how slippage works:
• Point (5,5) represents a balanced pool, trading around that point would incur little slippage in either direction.
• Point (~2,~9), The Green Dot, represents an out of balance pool with too much of asset X.
• Point (~9,~2), The Red Dot, represents an out of balance pool with too much of asset Y.
• Trading from equilibrium to either dot will incur slippage such that the amountOut will be less than the amountIn.
• Trading from either dot will incur slippage such that amountOut will be greater than the amountIn.
• We assume the red shaded area represents invalid trades for the spark-controller (based on maxSlippage) if the trade moves from any point on the curve near equilibrium to any point further from equilibrium.
It is likely that the Spark system will be a large participant in the pools the spark-controller is interacting with, which means that it is reasonable to consider the pools to be a relatively "low liquidity" environment, relative to the potential size of the trades. This will be bounded some by the Spark RateLimit contract, but moving the market with swaps should be considered likely for the spark-controller swaps.
Pairing sDAI and other Maker/Sky stable coins with stable coins in the Curve Stable Pools will have impact on the price peg of the Maker/Sky stable coins and thus, it should be desirable that the spark-controller system ideally improves the health of the Curve pools or at least does not harm it.
It should also be desirable, as partially expressed by the maxSlippage, that the swaps done by the RELAYER should benefit or at least not harm the spark-controller system (i.e. do not execute trades that cost the system "too much").
With this background in place, we can evaluate the efficacy of the maxSlippage protection with a couple of scenarios.
For ease of description, we will make a couple of assumptions:
• maxSlippage is 0.98e18 unless otherwise stated.
• The store_price function returns a 1:1 price pairing for the assets unless otherwise noted (so the only deviation from 1:1 pricing is due to Curve pool slippage).
• the pool is in equilibrium at the point (5,5).
• We are ignoring Curve fees for this analysis (so the only deviation from 1:1 pricing is due to Curve pool slippage).
Scenario 1: Imbalanced pool:
In this scenario, we assume that regular market forces have pushed the Pool into an imbalanced state, lets assume that current balance between (x,y) is skewed towards asset Y into the red zone past the green dot. Any trade that moves the balance towards equilibrium will be rewarded. Because our current pool balance is in the red zone, any RELAYER swap from asset Y to asset X will be blocked by maxSlippage because it would be more than a 2% discount. However, almost any RELAYER swap from asset X to asset Y will be accepted by the Controller since it would have a slippage above -2%.
If the RELAYER swaps enough asset Y to asset X to move the pool back into equilibrium, then it would be rewarded a bonus in amountOut. However, if the RELAYER trades even more of asset Y for asset X, such that the pool starts to be imbalanced in the other direction, the spark-controller will allow this too. Assuming a swap that leaves the pool containing more asset X than asset Y, the swap would still have slippage such that the amountOut is greater than the amountIn, but this second amountOut would be less than the first, balancing trade's amountOut because the Curve pool would reward it up to the equilibrium point, but then start punishing it for the portion of the trade that moves beyond that. The RELAYER's swap could entirely flip the pool with a trade that does not violate the maxSlippage protection effectively it would have an end state that is the reverse of the initial state. Visually we could say this trade moved all the way from the Green dot to the Red dot (or visa versa).
If the Curve pool is filling up with Asset X, it is likely that Asset X is loosing its value relative to Asset Y and because this swap changes the balance of the pool such that it ends up with more Asset Y, the spark-controller will accumulate Asset X, thus putting itself at risk of "holding the bag". Though if the price of Y is too high in Curve compared to other markets, the RELAYER may see an arbitrage opportunity.
Even setting aside this sort of more extreme market situation, allowing the RELAYER to move the market from one Dot to another is not the most efficient, profitable trade. The spark-controller is missing out on the slippage reward it would have received by moving the market from an imbalanced state to a balanced one. This lost profit is roughly amountIn * (percent market is imbalance + 100e18 - maxSlippage).
Scenario 2: De-pegging asset + Other pool whale.
This scenario shares some similar aspects to the first scenario, but includes a 3rd party actor who is also a large liquidity provider. In this scenario, we can assume there is a major de-peg event that is just starting.
The pool is still relatively in equilibrium. Seeing a trade from the RELAYER, the 3rd party calls remove_liquidity_one_coin to pull all their liquidity out in the form of asset X. Assuming they are large enough, this could swing the pool to be imbalanced with too much asset Y. This 3rd party would lose a quantity of asset X tokens due to slippage on this removal. If the reduction in quantity is less than the predicted reduction in value for asset X during a black swan de-peg and/or less than the cost of pulling out asset Y, the actor might choose to accept this loss. Further, arbitraging the pool back to equilibrium after the RELAYER's swap could help off set some of these costs. The RELAYER's trade could then swing the pool from a state where it had too much asset Y to one where it had too much asset X. The 3rd party could then use the received asset X to arbitrage the pool back to equilibrium, swapping their soon to be worth less asset X for asset Y. Lets outline the steps here:
1. The X/Y pool is at a 1:1 ratio.
2. A third-party liquidity provider decides to `remove_liquidity_one_coin` due to market conditions, removing X, which is not yet reflected in the Curve pool.
- Removing only one coin in large amounts will change the price and result in extra fees compared to removing both coins equally (the standard removal function).
3. The pool now contains more Y than X, meaning X has a higher price. (removing X here would be similar to buying X with Y).
4. The relayer wants to sell X or Y and is front-run by step 3.
- If selling Y for X, the relayer's swap would be blocked because of the `maxSlippage` constraint, so only possible to sell X.
- Selling X for Y, if the price after the trade returns to 1:1, the relayer would have made more money than without the front-running.
- However, if the relayer pushes the price in the other direction, the overall trade would still satisfy the `maxSlippage` constraint but with even less money returned for the swap.

## Recommendation
At a minimum, RELAYERs should have off-chain calculations to ensure they are swapping an amount that results in the "right amount" of slippage and setting a minAmount appropriately. Spark should also monitor RELAYER swaps to ensure they are performed in the correct way.
Onchain validation could look at the Pool balances before and after to determine whether a trade is making it healthier or less healthy as that is a measure for both whether the swap receives closer to the optimal amount of slippage and/or if the Pool is being utilized in such a way as to support the stability of DAI by pairing it in a healthy way with other stable coins.
