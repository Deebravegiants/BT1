# [M] Incorrect New Token Addition Logic in Multi-Asset Market

## Summary
Severity: Medium
Contest weight: 0.4375
Dataset id: 12793
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PRINT3R protocol has a core Market contract to maintain market-wide accounting. By design, it supports the trading of multiple assets under the same liquidity. In the process of analyzing the multi-asset support, we notice the new token addition logic can be improved. In the following, we show the implementation of the related routine, i.e., `addToken()`. As the name indicates, this routine is used to dynamically add a new token and accordingly support the share reallocation among supported tokens. However, it comes to our attention that the new token's pool is initialized (line 133) after the pool share reallocation (line 131). This is incorrect as the pool share allocation should be performed after the new token pool initialization.
```solidity
function addToken(
    MarketId _id,
    Pool.Config calldata _config,
    string memory _ticker,
    bytes calldata _newAllocations,
    bytes32 _priceRequestKey
) external onlyPoolOwner(_id) {
    Pool.GlobalState storage state = globalState[_id];
    if (!state.isMultiAsset) revert Market_SingleAssetMarket();
    if (state.assetIds.length() >= MAX_ASSETS) revert Market_MaxAssetsReached();
    bytes32 assetId = keccak256(abi.encode(_ticker));
    if (state.assetIds.contains(assetId)) revert Market_TokenAlreadyExists();
    Pool.validateConfig(_config);
    if (!state.assetIds.add(assetId)) revert Market_FailedToAddAssetId();
    state.tickers.push(_ticker);
    _reallocate(_id, _newAllocations, _priceRequestKey);
    Pool.initialize(marketStorage[_id][assetId], _config);
}
```

## Recommendation
Revise the above routine by initializing the new token pool before the pool share re-allocation.
