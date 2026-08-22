# [M] DDOS in BalLiquidityProvider

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-aura
Published: 2022-05-25
Source: https://github.com/code-423n4/2022-05-aura-findings/issues/285
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-aura/blob/4989a2077546a5394e3650bf3c224669a0f7e690/contracts/BalLiquidityProvider.sol#L56
https://github.com/code-423n4/2022-05-aura/blob/4989a2077546a5394e3650bf3c224669a0f7e690/contracts/BalLiquidityProvider.sol#L57


# Vulnerability details

## Impact
DDOS to liquidity providers in BalLiquidityProvider
## Proof of Concept


- bal is equal to the contract’s balance of the asset
https://github.com/code-423n4/2022-05-aura/blob/4989a2077546a5394e3650bf3c224669a0f7e690/contracts/BalLiquidityProvider.sol#L56

- bal is required to be equal to the input parameter _request.maxAmountsIn[i] :
https://github.com/code-423n4/2022-05-aura/blob/4989a2077546a5394e3650bf3c224669a0f7e690/contracts/BalLiquidityProvider.sol#L57

An attacker can front-run liquidity providers by sending 1 Wei of the asset to make the balance not equal to the input. This can be repeated and be used to impede the liquidity provider from using the function which will always revert since bal != _request.maxAmountsIn[i]


## Recommended Mitigation Steps
Balances shouldn't be required to be equal to an input variable. An attacker can always make the balance a little bigger.  This check should be removed or changed to require (bal >=  _request.maxAmountsIn[i]).
