# [H] Borrow index isn't updated correctly

## Summary
Severity: High
Contest weight: 0.7881
Dataset id: 22626
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Rebasing tokens are not supported for both collateral and borrowable assets in AAVE V2. stETH is currently the only rebasing token supported by AAVE V2, and it has specific implementations. Additionally, stETH cannot be borrowed; it can only be used as collateral. Previously, AMPL was the only rebasing token that was both supported as collateral and borrowable, but it is no longer supported. AMPL had different implementations compared to other generic Aave contracts like AToken and DebtToken. The same applies to Seismic's USDB and WETH, which are rebasing tokens.
https://docs.aave.com/developers/v/2.0/guides/ampl-asset-listing https://etherscan.io/address/0xbd233d4ffdaa9b7d1d3e6b18cccb8d091142893a#code (steth atoken specific implementation)
The rebasing rewards are reflected to the liquidityIndex as follows:
```solidity
// claimableAmount always has 18 decimals, since both USDB and WETH have 18 decimals
uint256 claimableAmount = (underlyingAsset == USDB || underlyingAsset == WETH)
    ? IERC20Rebasing(underlyingAsset).getClaimableAmount(address(this))
    : 0;
// only accrue native yield if there is something to be claimed
if (claimableAmount > 0) {
    uint256 totalPoolHoldings =
        IERC20(underlyingAsset).balanceOf(aTokenAddress) + // pool liquidity
        IERC20(reserve.stableDebtTokenAddress).totalSupply() + // total stable debt
        IERC20(reserve.variableDebtTokenAddress).totalSupply(); // total variable debt
    // express claimable amount as a percentage of pool assets and convert from wad to ray
    uint256 claimedInterestIndex =
        claimableAmount.wadDiv(totalPoolHoldings).wadToRay();
    // update pool liquidity index to reflect accrued native
    newLiquidityIndex = claimedInterestIndex.rayMul(newLiquidityIndex);
    reserve.liquidityIndex = uint128(newLiquidityIndex);
    require(newLiquidityIndex <= type(uint128).max,
        Errors.RL_LIQUIDITY_INDEX_OVERFLOW);
    // claim and send yield to the aToken
    IERC20Rebasing(underlyingAsset).claim(address(aTokenAddress),
        claimableAmount);
}
```
However, the borrowIndex is not updated as accordingly. The liquidityIndex updates assuming the rebase rewards will be back by borrowers. However, the borrowers are not encouraged to do it since the borrowIndex is NOT updated.
```solidity
if (scaledVariableDebt != 0) {
    uint256 cumulatedVariableBorrowInterest =
        MathUtils.calculateCompoundedInterest(
            reserve.currentVariableBorrowRate,
            timestamp
        );
    newVariableBorrowIndex =
        cumulatedVariableBorrowInterest.rayMul(variableBorrowIndex);
    require(
        newVariableBorrowIndex <= type(uint128).max,
        Errors.RL_VARIABLE_BORROW_INDEX_OVERFLOW
    );
    reserve.variableBorrowIndex = uint128(newVariableBorrowIndex);
}
```
liquidityIndex will be way ahead of the borrowIndex, which will mean that the supplier will assume that there are enough funds returned by the borrowers.
However, borrowers are not entitled to the extra borrowing APY that rebasing causes.
Additional read: https://ethereum.stackexchange.com/questions/154265/why-are-the-aave-v2-supply-and-borrow-index-rate-calculations-done-differently
Insolvency.

## Recommendation
Use NrETH, NrUSDB, the wrapped versions of rebasing tokens like wstETH if the rebasing points accounting works. That way the AAVE V2 code can be used without adding any extra code.
I think rebasing tokens can't work properly with AAVE V2/V3.
