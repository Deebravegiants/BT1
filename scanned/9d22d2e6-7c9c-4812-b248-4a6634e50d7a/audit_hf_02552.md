# [M] Stargate can not transfer asset amounts smaller than the conversion rate for the pool

## Summary
Severity: Medium
Contest weight: 0.2529
Dataset id: 13572
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Stargate pools have a concept of convert rate. It's calculated based on the sharedDecimals and localDecimals for a specific pool. For example, the DAI Pool has the sharedDecimals set to 6 while localDecimals is 18.
The convert rate is then: 10^(localDecimals - sharedDecimals) = 10^12.
Here is the DAI Pool on Ethereum and the convert rate logic inside the Pool contract.
Transferring an amount less than 10^12 on a pool with a convert rate different than with Stargate is not possible: https://github.com/stargate-protocol/stargate/blob/5f0dfd2/contracts/Router.sol#L126.
The amount needs to be a multiple of 10^12 and any dust amount is not transferred.
Looking at reserve rebalancing, incomingOrders for a chain are created even if the amounts are small: https://github.com/Phuture-Finance/phuture-v2-contracts/blob/0ee3b0b909d0c9795ffefdd377b8671888c3a85d/src/libraries/RebalancingLib.sol#L211.
During this first step of reserve rebalancing, incoming orders can be created and sent to a remote chain while the size of the trade is less than 10^12.
After all the orders are executed on the home chain, finishRebalancing() will be called to send the actual orders to all the remote chains. An order smaller than 10^12 can never be sent through Stargate.
This is an issue during reserve rebalancing and regular rebalancing.
Although it is even more likely to occur during the normal rebalancing on the remote chains, the following scenario highlights that there is a griefing concern as well.
In normal circumstances, reserve rebalancing will only occur if there is sufficient reserve so the issue for small amounts may not seem realistic.
However, an adversary can front-run the transaction that calls startReserveRebalancing() and redeem his shares from the reserve to intentionally leave a small amount of reserve to rebalance.
There is an additional broader concern that there is no minimum sell amount threshold, independent of Stargate. Orders with 1 wei of sell amount can be created. During order execution, if the price of the asset that is being sold is smaller than the asset being bought, the only way of executing this order is buying 0 amount. This leads to issues downstream. If this is the only sell order to generate a buy order for the remote chain, the finishOrderExecution() function will generate a PendingOrder with totalBought equal to zero.

## Recommendation
Not handling small amounts is a broad architectural problem. One recommendation for handling it is defaulting to sending a LayerZero message in case the Stargate swap cannot be executed so the incomingOrders of the destination chain get decremented and rebalancing can be finalized.
