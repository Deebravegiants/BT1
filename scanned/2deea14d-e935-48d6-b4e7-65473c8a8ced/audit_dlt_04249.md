# [M] `preview*` functions do not follow EIP5095

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/184
Type: sherlock-finding

## Details
JohnSmith

medium

# `preview*` functions do not follow EIP5095

## Summary
`previewDeposit`, `previewMint`, `previewRedeem`, `previewWithdraw` are not aware of slippage for swaps made to obtain tokens.
## Vulnerability Detail
Same issue for all of them, we take a look at `previewRedeem` in particular.
```solidity
src/tokens/ERC5095.sol
128:     function previewRedeem(uint256 s) public view override returns (uint256) {
129:         if (block.timestamp > maturity) {
130:             return s;
131:         }
132:         return IYield(pool).sellFYTokenPreview(Cast.u128(s));
133:     }
```

when we call this at `block.timestamp <= maturity` we get `IYield(pool).sellFYTokenPreview(Cast.u128(s))` called.
however when we call `redeem` we include 1% slippage i.e. on L298
```solidity
src/tokens/ERC5095.sol
294:                 uint128 returned = IMarketPlace(marketplace).sellPrincipalToken(
295:                     underlying,
296:                     maturity,
297:                     Cast.u128(s),
298:                     assets - (assets / 100)
299:                 );
```
as result `redeem` may return up 1% lower amount than stated by `previewRedeem`

according to EIP5095 https://eips.ethereum.org/EIPS/eip-5095
`previewRedeem`
> MUST return as close to and no more than the exact amount of underliyng that would be obtained in a redeem call in the same transaction. I.e. redeem should return the same or more underlyingAmount as previewRedeem if called in the same transaction.

## Impact

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/184_
