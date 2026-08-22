# [M] `WiseOracleHub.getTokensPriceFromUSD()`skips TWAP computation which permits the use of price even if the difference >`ALLOWED_DIFFERENCE`

## Summary
Severity: Medium
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-17
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/47
Type: hats-finding

## Details
**Github username:** @@Tri-pathi
**Twitter username:** @0xTripathi
**Submission hash (on-chain):** 0xeebe2b67d0b63b921e9b6c32ecb4d41eb3c6a2e12dbfc2d4b7e613094383eb66
**Severity:** medium

**Description:**
**Description**\

`WiseOracleHub.getTokensPriceFromUSD()`skips TWAP computation which permits the use of price even if the difference >`ALLOWED_DIFFERENCE`  

**Attack Scenario**\


**Attachments**

1. **Proof of Concept (PoC) File**
`WiseOracleHub.getTokensPriceFromUSD()` Converts USD value of a token into token amount with a current price. 
```solidity
    function getTokensPriceFromUSD(
        address _tokenAddress,
        uint256 _usdValue
    )
        external
        view
        returns (uint256)
    {
        return getTokensFromETH(
            _tokenAddress,
            _usdValue
                * 10 ** _decimalsUSD
                / getETHPriceInUSD()
        );
    }
```
`getTokensFromETH()` calls `latestResolver()` where TWAP logic implemented to check the difference between twap price and chainlink price is with in the `ALLOWED_DIFFERENCE`

If `_tokenAddress=WETH_ADDRESS`, latestResolver() skips these checks and return amount directly
```solidity
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/47_
