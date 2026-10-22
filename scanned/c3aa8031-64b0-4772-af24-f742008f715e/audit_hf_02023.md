# [M] MissingCheckForActiveL2Sequencerin calculateArbAmount()

## Summary
Severity: Medium
Contest weight: 0.4602
Dataset id: 11553
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The calculateArbAmount() function converts an amount of ETH (in Wei) to its equivalent amount in ARB tokens, using the latest exchange rates for ETH/USD and ARB/USD provided by Chainlink price feeds:
```solidity
function calculateArbAmount(uint256 _ethAmountInWei) internal view returns (uint256) {
    // Fetch the ETH to USD price with 8 decimal places
    (, int256 ethUsdPrice,,,) = IChainLinkAggregator(
        comptroller.getEthUsdAggregator()
    ).latestRoundData();
    // Fetch the ARB to USD price with 8 decimal places
    (, int256 arbUsdPrice,,,) = IChainLinkAggregator(arbUsdAggregator).latestRoundData();
    // Convert the ETH amount to USD
    // _ethAmountInWei is in wei, ethUsdPrice has 8 decimal places.
    // We multiply by 10^10 to adjust the final result to have 18 decimal
    // places for ARB.
    uint256 usdAmount = (_ethAmountInWei * uint256(ethUsdPrice)) / rewardTokenDecimals;
    // Convert the USD amount to ARB
    // usdAmount is in USD with 18 decimals, arbUsdPrice has 8 decimal
    // places.
    // The result is in ARB's smallest unit (like wei for ETH).
    uint256 arbAmount = (usdAmount * rewardTokenDecimals) / uint256(arbUsdPrice);
    return arbAmount;
}
```
This function does not check if the Sequencer is active. Optimistic rollup protocols move all execution of the layer 1 (L1) Ethereum chain, complete execution on a layer 2 (L2) chain, and return the results of the L2 execution back to the L1. These protocols have a sequencer that executes and rolls up the L2 transactions by batching multiple transactions into a single transaction. If a sequencer becomes unavailable, it is impossible to access read/write APIs that consumers are using and applications on the L2 network will be down for most users without interacting directly through the L1 optimistic rollup contracts. The L2 has not stopped, but it would be unfair to continue providing service on your applications when only a few users can use them.

If the Arbitrum Sequencer goes down, oracle data will not be kept up to date, and the price could become stale.

## Recommendation
Consider implementing logic to revert the execution when the price cannot be fetched. Check this example here.
