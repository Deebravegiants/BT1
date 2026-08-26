# [M] Incorrect consideration of `ONE_YEAR` leading to incorrect `APR RESTRICTION_FACTOR` and `PRECISION_FACTOR_YEAR`

## Summary
Severity: Medium
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-17
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/41
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Twitter username:** 0xRizwann
**Submission hash (on-chain):** 0x06b2d2232be162da245b03d2fd8297965729b3e93ec5560a8fc277ad391143ce
**Severity:** medium

**Description:**
**Description**\

*This is actually a low severity issue submitted with the intent the protocol team should fix in contracts.*

In `WiseLendingDeclaration.sol`, `ONE_YEAR` is considered as `52 weeks` which is equal to 364 days in calender year.


```solidity
    uint256 internal constant ONE_YEAR = 52 weeks;
```

This constant is further used in calculating the `PRECISION_FACTOR_YEAR`


```solidity
    uint256 internal constant PRECISION_FACTOR_YEAR = PRECISION_FACTOR_E18 * ONE_YEAR;

```

Now, `PRECISION_FACTOR_YEAR ` is further used in calculating the `RESTRICTION_FACTOR` which is an APR restriction factor.

```solidity
    uint256 internal constant RESTRICTION_FACTOR = 10
        * PRECISION_FACTOR_E36
        / PRECISION_FACTOR_YEAR;

```

`RESTRICTION_FACTOR` is extensively used in various functions in contracts.


With current implementation of 52 weeks or 364 days, the precision calculated will be incorrect.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/41_
