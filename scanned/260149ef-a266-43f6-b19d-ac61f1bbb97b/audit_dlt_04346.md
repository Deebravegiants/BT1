# [M] AssetManager.removeToken() should check whether getPoolBalance() == 0

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/147
Type: sherlock-finding

## Details
GimelSec

medium

# AssetManager.removeToken() should check whether getPoolBalance() == 0

## Summary

`AssetManager.removeToken(token)` would set `supportedMarkets[token]` to false. It causes assets to be frozen, if there are tokens that haven't been withdrawn from money markets. 

## Vulnerability Detail

`AssetManager.removeToken()` is a simple method to disable a market-supported token in `AssetManager`. It would set `supportedMarkets[token]` to false. Thus, `AssetManager.isMarketSupported(token)` will return false.

```solidity
    function removeToken(address tokenAddress) external override onlyAdmin {
        bool isExist = false;
        uint256 index;
        uint256 supportedTokensLength = supportedTokensList.length;

        for (uint256 i = 0; i < supportedTokensLength; i++) {
            if (tokenAddress == address(supportedTokensList[i])) {
                isExist = true;
                index = i;
                break;
            }
        }

        if (isExist) {
            supportedTokensList[index] = supportedTokensList[supportedTokensLength - 1];
            supportedTokensList.pop();
            supportedMarkets[tokenAddress] = false;
        }
    }
```

```solidity
    function isMarketSupported(address tokenAddress) public view override returns (bool) {
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/147_
