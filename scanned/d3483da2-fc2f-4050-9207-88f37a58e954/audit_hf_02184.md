# [H] Incorrect Calculation of getNewMinimumRatio()

## Summary
Severity: High
Contest weight: 0.6357
Dataset id: 12177
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To facilitate the code organization and contain contract code size for deployment, the handle.fi protocol has a library contract named VaultLibrary. This library contract provides read-only functions to calculate vault data such as the collateral ratio, the equivalent ETH value of collateral/debt at the current exchange rates, weighted fees, etc. In the following, we examine a specific library function getNewMinimumRatio(). This function is designed to returns the new minimum vault ratio due to a collateral deposit or withdraw. It is mainly used for checking the collateralization ratio is valid before performing an operation. Our analysis shows the current implementation is only appropriate when there is a collateral deposit. However, it is flawed when there is a collateral withdraw.
```solidity
function getNewMinimumRatio(
    address account,
    address fxToken,
    address collateralToken,
    uint256 collateralAmount,
    uint256 collateralQuote,
    bool isDeposit
) public view override returns (uint256 ratio, uint256 newCollateralAsEther) {
    uint256 currentMinRatio = getMinimumRatio(account, fxToken);
    uint256 vaultCollateral = getTotalCollateralBalanceAsEth(account, fxToken);
    // Calculate new vault collateral from deposit amount.
    newCollateralAsEther = isDeposit
        ? vaultCollateral.add(
            collateralQuote.mul(collateralAmount).div(
                getTokenUnit(collateralToken)
            )
        )
        : vaultCollateral.sub(
            collateralQuote.mul(collateralAmount).div(
                getTokenUnit(collateralToken)
            )
        );
    uint256 depositCollateralMintCR = handle.getCollateralDetails(collateralToken).mintCR;
    if (currentMinRatio == 0) {
        ratio = depositCollateralMintCR.mul(1 ether).div(100);
    } else {
        /* Ratio for the current share of minimum collateral ratio due to the deposit change (i.e. if vault holds $50 and the new deposit is $50, this value is 50% expressed as 0.5 ether). */
        uint256 oldCollateralMintRatio = vaultCollateral.mul(1 ether).div(newCollateralAsEther);
        // Calculate new minimum ratio using the CR ratio above.
        ratio = currentMinRatio
            .mul(oldCollateralMintRatio)
            .div(1 ether)
            .add(
                uint256(1 ether)
                .sub(oldCollateralMintRatio)
                .mul(depositCollateralMintCR)
                .div(1 ether)
            );
    }
}
```
Specifically, the internal variable oldCollateralMintRatio is used to represent the ratio for the current share of minimum collateral ratio due to the deposit change. In a collateral deposit scenario, this variable is no larger than 1 eth, which yields the proper ratio. However, in a collateral withdraw scenario, this variable is no smaller than 1 eth, which can easily result in reverting the execution due to the SafeMath operation on uint256(1 ether).sub(oldCollateralMintRatio) (lines 565-566).

## Recommendation
Accommodate both scenarios of collateral changes in getNewMinimumRatio().
