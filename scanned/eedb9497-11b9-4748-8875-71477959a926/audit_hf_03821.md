# [M] getPriceFromChainlink() doesn't check If Ar-

## Summary
Severity: Medium
Contest weight: 0.3922
Dataset id: 20051
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When utilizing Chainlink in L2 chains like Arbitrum, it's important to ensure that the prices provided are not falsely perceived as fresh, even when the sequencer is down. This vulnerability could potentially be exploited by malicious actors to gain an unfair advantage. There is no check: getPriceFromChainlink

```solidity
function getPriceFromChainlink(address base, address quote) internal view returns (uint256) {
    (int256 price,) = registry.latestRoundData(base, quote);
    require(price > 0, "invalid price");
    // Extend the decimals to 1e18.
    return uint256(price) * 10 ** (18 - uint256(registry.decimals(base, quote)));
}
```

could potentially be exploited by malicious actors to gain an unfair advantage.

## Recommendation
code example of Chainlink: https://docs.chain.link/data-feeds/l2-sequencer-feeds#example-code
