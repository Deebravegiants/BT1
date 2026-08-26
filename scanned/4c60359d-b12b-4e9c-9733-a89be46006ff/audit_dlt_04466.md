# [M] crab token price is using totalSupply, which is vulnerable to manipulation.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/163
Type: sherlock-finding

## Details
ctf_sec

medium

# crab token price is using totalSupply, which is vulnerable to manipulation.

## Summary

crab token price is using totalSupply, which is vulnerable to manipulation.

## Vulnerability Detail

If we look into the function _checkCrabPrice, the implementation is below:

```solidity
    function _checkCrabPrice(uint256 _price) internal view {
        // Get twap
        uint256 squeethEthPrice = IOracle(oracle).getTwap(ethSqueethPool, sqth, weth, auctionTwapPeriod, true);
        uint256 usdcEthPrice = IOracle(oracle).getTwap(ethUsdcPool, weth, usdc, auctionTwapPeriod, true);
        (,, uint256 collateral, uint256 debt) = ICrabStrategyV2(crab).getVaultDetails();
        uint256 crabFairPrice =
            ((collateral - ((debt * squeethEthPrice) / 1e18)) * usdcEthPrice) / ICrabStrategyV2(crab).totalSupply();
        crabFairPrice = crabFairPrice / 1e12; //converting from units of 18 to 6
        require(_price <= (crabFairPrice * (1e18 + otcPriceTolerance)) / 1e18, "Crab Price too high");
        require(_price >= (crabFairPrice * (1e18 - otcPriceTolerance)) / 1e18, "Crab Price too low");
    }
```

note the crab price implementation:

```solidity
uint256 crabFairPrice =
    ((collateral - ((debt * squeethEthPrice) / 1e18)) * usdcEthPrice) / ICrabStrategyV2(crab).totalSupply();
```

it is using the crab totalSupply, which make the crab token price vulnerable to manipulation. 

This is the crab token on mainnet 

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/163_
