# [M] `mint` does not mint

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/185
Type: sherlock-finding

## Details
JohnSmith

medium

# `mint` does not mint

## Summary
`mint` does not mint anything when called on `block.timestamp == maturity`
## Vulnerability Detail
`mint()` call on `block.timestamp == maturity`
will lead to `assets = 0` 

```solidity
src/tokens/ERC5095.sol
186:         uint128 assets = Cast.u128(previewMint(s));
```

```solidity
src/tokens/ERC5095.sol
118:     function previewMint(uint256 s) public view returns (uint256) {
119:         if (block.timestamp < maturity) {
120:             return IYield(pool).buyFYTokenPreview(Cast.u128(s));
121:         }
122:         return 0;
123:     }
```

which will lead to zero transfer and zero swap

```solidity
src/tokens/ERC5095.sol
187:         Safe.transferFrom(
188:             IERC20(underlying),
189:             msg.sender,
190:             address(this),
191:             assets
192:         );
193:         // consider the hardcoded slippage limit, 4626 compliance requires no minimum param.
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/185_
