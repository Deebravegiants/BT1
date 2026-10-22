# [M] Improper Annual Fee Collection in xGoldBundle

## Summary
Severity: Medium
Contest weight: 0.4178
Dataset id: 13136
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the audited Swarm Bundles protocol, there is a key xGoldBundle contract that represents a bundle of xGold, where 1 token represents 1 ounce (consisting of xGoldOz and xGoldKg). While examining the annual fee collection for the bundle management, we notice the logic may be improved.

In the following, we show the code snippet of the affected addNewAssets() routine. This routine has a rather straightforward logic in adding new asset to the bundle. However, the fee is collected after the asset bundle token is minted, which changes the total supply. We notice the annual fee collection depends on the total supply for the fee calculation. With that, there is a need to collect annual fee before the new bundle token is minted.

```solidity
function addNewAssets(Asset[] calldata _assets) external {
    uint256 toMint;
    for (uint256 i = 0; i < _assets.length; ) {
        _onlyWhitelistedAsset(_assets[i].assetAddress);
        toMint += bundleStorage.getGoldPrice(_assets[i].assetAddress);
        unchecked {
            ++i;
        }
    }
    mint_(msg.sender, toMint);
    _updateAnnualFeesRate();
    _depositAssets(_assets);
}
```

Public

## Recommendation
Revisit the above logic to update annual fee before new bundle token is minted. Note the same issue also affects another related routine withdrawAssets().
