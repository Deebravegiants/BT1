# [M] Virtual swap balances don't take into account

## Summary
Severity: Medium
Contest weight: 0.5930
Dataset id: 20033
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Virtual swap balances don't take into the fact that an exchange between the collateral token and the virtual token is taking place, necessitating an exchange rate. Virtual position impacts are all based on the virtual token being the same token as the market's index token. With virtual swap impacts, they're not the same token — the market token is a market collateral token, and the virtual token is some other token, which likely has a different price. For example, the README mentions ETH/USDC as ETH/USDT, where USDC is paired with USDT. USDC and USDT sound like they should be equivalent, but looking at the monthly chart of the exchange rate between the two, it has been between 0.8601 and 1.2000 — a 20% difference at the margins. Further, if one of them were to de-peg, the difference may be even larger and for a much longer period of time. This applies to swaps, as well as to position changes, since those also track virtual swap inventory, since the balance is changing. Orders on some markets will get larger/smaller virtual discounts/penalties than they should, as compared to other markets using the same virtual impact pool. In addition to the basic accounting/fee issues associated with the difference, if the price difference is large enough, someone can swap through it on the market where the impact is smaller due to the exchange rate in order to push the impact more negative, and then simultaneously swap through the other market, where the same amount of funds would result in a larger positive impact than was incurred negatively on the other market, unfairly draining any impact discounts available to legitimate traders. The delta being applied is a token amount:
```solidity
// File: gmx-synthetics/contracts/swap/SwapUtils.sol : SwapUtils._swap()
MarketUtils.applyDeltaToPoolAmount(
    params.dataStore,
    params.eventEmitter,
    _params.market.marketToken,
    _params.tokenIn,
    (cache.amountIn + fees.feeAmountForPool).toInt256()
);
// the poolAmountOut excludes the positive price impact amount
// as that is deducted from the swap impact pool instead
MarketUtils.applyDeltaToPoolAmount(
```
gmx-synthetics/contracts/swap/SwapUtils.sol#L273-L293  
And is stored unaltered as the virtual amount:
```solidity
// File: gmx-synthetics/contracts/market/MarketUtils.sol : MarketUtils.applyDeltaToVirtualInventoryForSwaps()
function applyDeltaToVirtualInventoryForSwaps(
    DataStore dataStore,
    EventEmitter eventEmitter,
    address market,
    address token,
    int256 delta
) internal returns (bool, uint256) {
    bytes32 marketId = dataStore.getBytes32(Keys.virtualMarketIdKey(market));
    if (marketId == bytes32(0)) {
        return (false, 0);
    }

    uint256 nextValue = dataStore.applyBoundedDeltaToUint(
        Keys.virtualInventoryForSwapsKey(marketId, token),
        delta
    );

    MarketEventUtils.emitVirtualSwapInventoryUpdated(eventEmitter, market, token, marketId, delta, nextValue);

    return (true, nextValue);
}
```
gmx-synthetics/contracts/market/MarketUtils.sol#L1471-L1491  
The same is true for deposits, decreases, increases, and withdrawals.

## Recommendation
Use oracle prices and convert the collateral token to the specific virtual token
