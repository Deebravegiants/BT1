# [M] Managers can deposit NFTs worth nothing

## Summary
Severity: Medium
Contest weight: 0.5932
Dataset id: 22931
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Managers can allow Velodrome/UnsiwapV3 NFT positions as deposit assets and deposit NFT positions worth nothing while still minting shares. The manager has the possibility of adding all of the valid assets as deposit assets to a pool, including NFT assets such as Velodrome/UnsiwapV3 NonfungiblePositionManager contracts. If such assets are deposited the function PoolLogic::_depositFor will calculate their value in dollars incorrectly. The dollar value is calculated via a call to PoolManagerLogic::assetValue:
```solidity
uint256 usdAmount = IPoolManagerLogic(poolManagerLogic).assetValue(_asset, _amount);
```
which in turn retrieves the dollar value of the asset via:
```solidity
function assetValue(address asset, uint256 amount) public view override returns (uint256 value) {
    uint256 price = IHasAssetInfo(factory).getAssetPrice(asset);
    uint256 decimals = assetDecimal(asset);
    value = price.mul(amount).div(10 ** decimals);
}
```
This is problematic because for Velodrome/UniV3 NFT positions the asset price returned via PoolFactory::getAssetPrice() is always 1e18. Because of this, it's possible for a manager to:
1. Allow NFT liquidity position as valid deposit assets
2. Craft an NFT position with 0 or almost zero liquidity
3. Deposit the NFT position via PoolLogic::_depositFor by passing as amount the ID of the NFT position
4. The NFT position will always be valued based on its ID, for instance a token with ID 500000 would be valued at 500000/1e18 $
5. More shares can be minted than the actual value of the NFT position
This makes it possible for a manager to mint shares while depositing an asset that is worth nothing. A malicious manager can mint a number of shares higher than the value of the asset deposited. The ID of the NFT position must be bigger than 100000 for this to be meaningful. This wouldn't be possible right now with Velodrome NFT positions because the current ID is lower than 100000. This would be possible with UniswapV3 NFT positions but the current ID is 500000, which would mint an equivalent of 500000/1e18 $ worth of shares which is extremely little.

## Recommendation
There should be some sort of whitelist on what tokens are allowed to be added as deposit tokens.
