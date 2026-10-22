# [M] **Liquidations will be frozen, when the chainlink oracle goes offline**

## Summary
Severity: Medium
Chain: Smart contract
Component: VMEX
Published: 2023-06-19
Source: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/3
Type: hats-finding

## Details
**Github username:** @https://github.com/maarcweiss
**Submission hash (on-chain):** 0x6bddb0c819575a51ced25c0fffb628214677f641f66c532e0c3b43e5a6b7d969
**Severity:** medium severity

**Description:**
**Liquidations will be frozen, when the chainlink oracle goes offline**

In certain exceptional scenarios, such as when oracles go offline/paused  liquidations and borrowing will be temporarily suspended.

When liquidator want to `liquidationCall()` (or borrower `borrow()` ), an account because of bad debt, it will check the `_calculateAvailableCollateralToLiquidate()` and loop over it, fetching during calculation `vars.collateralPrice = oracle.getAssetPrice(collateralAsset);` As there is no fallback if chainlink fails (due to offline/paused), the function call will revert and liquidations will be paused.

## **SEVERITY**

Impact high, likelihood low = Medium

During critical periods, there is a risk that liquidations may not be feasible when they are most needed by the protocol. This can lead to a situation where the value of users' assets declines below their outstanding debts, effectively disabling any motivation for liquidation. Consequently, this can potentially push the protocol into insolvency, posing significant challenges and potential financial instability.

## **A LINK TO THE GITHUB ISSUE**

https://github.com/VMEX-finance/vmex/blob/b0dc00c5dd6bdcac05827128d14dcdc730f19e1c/packages/contracts/contracts/protocol/oracles/VMEXOracle.sol#L208-L230

## **SOLUTION**

Implement a protective measure to mitigate this potential risk. For example, enclose chainlink’s get price function within a try-catch block.
