# [M] Users can receive zero `issuance` or `collateral` tokens via buy or sell orders in `FundingManager`

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-19
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/157
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0xf491f17cd7e6c05e14463574be4b18adb15d2c3e013c38a0a84045248e672c9f
**Severity:** medium

**Description:**
## Impact
Users can lose expected value when `BancorFormula` returns zero: this can happen when `issuance` or `collateral` token supply is magnitudes bigger than the other or upon owner set virtual supply changes or when the user's amount is a lot smaller than the total supply

## Description
When in the `issuance` - `collateral` supply ratio, one of the tokens is a few orders of magnitude higher in one side (doesn't take a lot), problems can arise from rounding with `BancorFormula` calculations. One of them is rounding to zero upon `buy` and `sell` orders of funding manager, which will lead to the user not getting any tokens out, but transferring their `collateral` tokens in or burning their `issuance` tokens.

`FM_BC_Bancor_Redeeming_VirtualSupply_v1.sol` - `_issuanceTokensFormulaWrapper()`
```solidity
    function _issueTokensFormulaWrapper(uint _depositAmount)
        internal
        view
        override(BondingCurveBase_v1)
        returns (uint mintAmount)
    {
        // Calculate mint amount through bonding curve
        uint decimalConvertedMintAmount = formula.calculatePurchaseReturn(
            // decimalConvertedVirtualIssuanceSupply
            FM_BC_Tools._convertAmountToRequiredDecimal(
                virtualIssuanceSupply, issuanceTokenDecimals, eighteenDecimals
            ),
            // decimalConvertedVirtualCollateralSupply
            FM_BC_Tools._convertAmountToRequiredDecimal(
                virtualCollateralSupply,
                collateralTokenDecimals,
                eighteenDecimals
            ),
            reserveRatioForBuying,
            // decimalConvertedDepositAmount
            FM_BC_Tools._convertAmountToRequiredDecimal(
                _depositAmount, collateralTokenDecimals, eighteenDecimals
            )
        );
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/157_
