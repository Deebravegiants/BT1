# [M] Only one lien can be created per collateral, vault, and strategy

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-astaria
Published: 2022-11-07
Source: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/275
Type: sherlock-finding

## Details
Jeiwan

medium

# Only one lien can be created per collateral, vault, and strategy

## Summary
Only one lien can be created per collateral, vault, and strategy
## Vulnerability Detail
Lien ID is generated based on: collateral ID, vault address, loan terms, and strategy root ([LienToken.sol#L264-L279](https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/LienToken.sol#L264-L279)). This doesn't include any lien-specific fields, which means duplicate are possible. However, there's no check for whether a lien ID already exists, only a check for the number of liens already created ([LienToken.sol#L282-L285](https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/LienToken.sol#L282-L285)). In case a duplicate lien ID is generated, the `_mint` function will revert with "ALREADY_MINTED" error ([LienToken.sol#L289](https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/LienToken.sol#L289)).
## Impact
Users cannot take multiple loans for the same collateral token in the same vault and under the same strategy.
## Code Snippet
[LienToken.sol#L264-L303](https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/LienToken.sol#L264-L303):
```solidity
lienId = uint256(
  keccak256(
    abi.encodePacked(
      abi.encode(
        bytes32(collateralId),
        params.vault,
        WETH,
        params.terms.maxAmount,
        params.terms.rate,
        params.terms.duration,
        params.terms.maxPotentialDebt
      ),
      params.strategyRoot
    )
  )
);

//0 - 4 are valid
require(
  uint256(liens[collateralId].length) < MAX_LIENS,
  "too many liens active"
);

```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/275_
