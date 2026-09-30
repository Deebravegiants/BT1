# [M] Fetching indexToken.balanceOf() will always revert for BTC market

## Summary
Severity: Medium
Contest weight: 0.4308
Dataset id: 9797
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
// PerpetualVault.sol::initialize()
function initialize(
    address _market,
    address _keeper,
    address _treasury,
    address _gmxProxy,
    address _vaultReader,
    uint256 _minDepositAmount,
    uint256 _maxDepositAmount,
    uint256 _leverage
  ) external initializer {
...SNIP...

    indexToken = marketInfo.indexToken;

...SNIP...
  }

// VaultReader.sol::getMarket()
function getMarket(address market) public view returns (MarketProps memory) {
    return gmxReader.getMarket(address(dataStore), market);
  }
```
Due to the BTC/USD market returning a non-contract address as indexToken, any calls to balanceOf() in PerpetualVault.sol revert, rendering the contracts incompatible with this key GMX market.

When a PerpetualVault is initialized, the indexToken address is set by calling getMarket() from the GMXReader:

According to the README, these contracts should be compatible with wBTC (i.e. the BTC/USD GMX market). However, in the BTC/USD market, marketInfo.indexToken is not a contract, so calling balanceOf() will revert.

Here's the indexToken address for the BTC/USD market on Arbitrum: https://arbiscan.io/address/0x47904963fc8b2340414262125af798b9655e58cd

indexToken.balanceOf() is used throughout the PerpetualVault.sol contract making Gamma's implementation incompatible with this key market.

Contracts incompatible with key GMX market.

## Recommendation
Consider using the long token instead of the index token for these markets, however, this can cause issues if you ever want to launch on markets where the long token doesn't equal the index token.
