# [H] Incorrect assessment of isEthVerified can lead to DOS in Ibo contract

## Summary
Severity: High
Chain: Smart contract
Component: Convergence-Finance---IBO
Published: 2023-09-04
Source: https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/issues/38
Type: hats-finding

## Details
**Github username:** @neumoxx
**Submission hash (on-chain):** 0x860a8254179ddf53471d34ecbba253588dfa8b0c216bfdfdf2d352e93ed00d5c
**Severity:** high

**Description:**
## Vulnerability Report
**Description**
Function `_postTreatmentAndVerifyEth` does an incorrect assessment of wether `isEthVerified` is true or false. It considers it to be true if `isStalePrice == true`, but it makes no sense, as it should be when the price is not stale.
The following line:
```solidity
isEthVerified = isOracleNotToLow && isOracleNotToHigh && isStalePrice;
```

Considers `isEthVerified` to be true if:
* Price form oracle is not too low AND
* Price form oracle is not too high AND
* Price form oracle is stale

The line should instead be:
```solidity
isEthVerified = isOracleNotToLow && isOracleNotToHigh && !isStalePrice;
```

**Attack Scenario**
As seen in function `_postTreatmentAndVerifyEth`:
https://github.com/Cvg-Finance/hats-audit/blob/da48577d2f42fa8c2e35bb7223208ea6ba88012e/contracts/Oracles/CvgOracle.sol#L164C14-L188

`isEthVerified` is wrongly calculated when function param `isEthPriceRelated` is true.

`_postTreatmentAndVerifyEth` is called by functions:
* _getV3Price
* _getV2Price
* _getCrvPoolPrice
* _getCrvPoolTricrypto

In the last one, the value for `isEthPriceRelated` is hardcoded as false, so it is not a problem. But the other three are called in `_getPriceOracle` passing in the value of `oracleParams.isEthPriceRelated`.

`_getPriceOracle` is called (among others) by function `_getAndVerifyOracleAndAggregatorPrices`:

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/issues/38_
