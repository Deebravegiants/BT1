# [M] VMEX would overvalue collateral if if the token's USD price feed's `decimals != 8`

## Summary
Severity: Medium
Chain: Smart contract
Component: VMEX
Published: 2023-06-19
Source: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/13
Type: hats-finding

## Details
**Github username:** @abhishekvispute
**Submission hash (on-chain):** 0xb0e84c6d8e6ff1df0dc79d11d6db45ea73ae669287a9d0a9706333c85878389e
**Severity:** medium severity

**Description:**
### Description : 
VMEX makes the assumption that all USD feeds would be of 8 decimals, and have not handled price feed decimals anywhere explicitly, considering it would always be compared in the same denomination of base currency.
However this is not always the case, sometimes chainlink price feeds for USD have decimals ≠8 
For example, AMPL/USD on mainnet has 18 decimals
https://etherscan.io/address/0xe20CA8D7546932360e37E9D72c1a47334af57706#code

Hence it is not guaranteed from the chainlink side that the constraint of decimals being 8 is always satisfied.

In some places where this is not considered, 
https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/blob/fb396a3fa412e643de7d8a1fd8a0268ab3a2f993/packages/contracts/contracts/protocol/oracles/VelodromeOracle.sol#L49

https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/blob/fb396a3fa412e643de7d8a1fd8a0268ab3a2f993/packages/contracts/contracts/protocol/libraries/logic/GenericLogic.sol#L181

## Attack Scenario: 
Deposit Token (eg: AMPL), Borrow more than allowed since the collateral value is calculated incorrectly 

## Likelihood 
Considering that this requires the VMEX team to allow such a token, this is not a high likelihood, however, it is not a rare occurrence as well, since AAVE themselves support AMPL on mainnet.

## Recommendation: 
Either normalize prices in `getAssetPrice()` explicitly to base asset decimals 

or 

Verify inside `setAssetSources()` that decimals of price feed are equal to base asset decimals only
