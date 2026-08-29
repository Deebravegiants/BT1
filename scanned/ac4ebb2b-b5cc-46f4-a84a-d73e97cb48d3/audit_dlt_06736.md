# [H] Oracle price can be manipulated

## Summary
Severity: High
Chain: Smart contract
Component: 2024-03-abracadabra-money
Published: 2024-03-11
Source: https://github.com/code-423n4/2024-03-abracadabra-money-findings/issues/75
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-03-abracadabra-money/blob/main/src/oracles/aggregators/MagicLpAggregator.sol#L42-L45


# Vulnerability details

## Impact
Oracle price can be manipulated. 

## Proof of Concept
MagicLpAggregator uses pool reserves to calculate the price of the pair token,
```solidity
    function _getReserves() internal view virtual returns (uint256, uint256) {
        (uint256 baseReserve, uint256 quoteReserve) = pair.getReserves();
    }

    function latestAnswer() public view override returns (int256) {
        uint256 baseAnswerNomalized = uint256(baseOracle.latestAnswer()) * (10 ** (WAD - baseOracle.decimals()));
        uint256 quoteAnswerNormalized = uint256(quoteOracle.latestAnswer()) * (10 ** (WAD - quoteOracle.decimals()));
        uint256 minAnswer = baseAnswerNomalized < quoteAnswerNormalized ? baseAnswerNomalized : quoteAnswerNormalized;

>>      (uint256 baseReserve, uint256 quoteReserve) = _getReserves();
        baseReserve = baseReserve * (10 ** (WAD - baseDecimals));
        quoteReserve = quoteReserve * (10 ** (WAD - quoteDecimals));
        return int256(minAnswer * (baseReserve + quoteReserve) / pair.totalSupply());
    }
```
however reserve values can be manipulated. For example, an attacker can use a flash loan to inflate the pair price, see coded POC below

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "utils/BaseTest.sol";
import "oracles/aggregators/MagicLpAggregator.sol";

// import "forge-std/console2.sol";
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-03-abracadabra-money-findings/issues/75_
