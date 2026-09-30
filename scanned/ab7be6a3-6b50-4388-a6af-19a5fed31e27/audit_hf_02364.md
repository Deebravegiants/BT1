# [M] Revisited New Asset Support in PriceFeed

## Summary
Severity: Medium
Contest weight: 0.4226
Dataset id: 12794
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the Market support in PRINT3R allows for the trading of multiple assets under the same liquidity. With that, the related oracle is required to dynamically add new token to query token prices. Our analysis shows the current oracle needs to be improved when adding a new token. In the following, we show the implementation of the related routine `supportAsset()`. For the new token, it basically maintains the correct mapping from the new token to the related pricing strategy (line 167). However, it forgets to maintain the related token decimals, i.e., `tokenDecimals[_ticker] = _tokenDecimals`. The lack of the new token's decimals will make the base unit of queried token price unavailable and possibly revert the oracle operation.
```solidity
function supportAsset(string memory _ticker, SecondaryStrategy calldata _strategy, uint8 _tokenDecimals) external onlyRoles(_ROLE_0) {
    bytes32 assetId = keccak256(abi.encode(_ticker));
    if (assetIds.contains(assetId)) return; // Return if already supported
    bool success = assetIds.add(assetId);
    if (!success) revert PriceFeed_AssetSupportFailed();
    strategies[_ticker] = _strategy;
    tokenDecimals[_ticker] = _tokenDecimals;
    emit AssetSupported(_ticker, _tokenDecimals);
}
```

## Recommendation
Improve the above-mentioned routine to properly maintain the decimals for the new token asset.
