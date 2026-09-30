# [M] Withdrawing all assets from TeaHouse will fail

## Summary
Severity: Medium
Contest weight: 0.5932
Dataset id: 22619
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Withdrawing all assets from TeaHouse will fail due to overflow  
When deactivating or liquidating, the internal function _withdrawAllFromTargets is called which further invokes _withdrawFromTarget with the wildcard number type(uint256).max to indicate that all possible assets must be removed  
```solidity
function _withdrawAllFromTargets(address[] memory withdrawTargets, bytes memory data) internal {
    uint256 numWithdrawTargets = withdrawTargets.length;
    for (uint256 i; i < numWithdrawTargets; ++i) {
        address withdrawTarget = withdrawTargets[i];
        if (!s_withdrawTargets.contains(withdrawTarget)) revert InvalidWithdrawTarget(withdrawTarget);
        _withdrawFromTarget(type(uint256).max, withdrawTarget, data);
    }
}
```
For other integrations, this wildcard number is handled by taking minimum with the total available assets in the respective protocols. But for TeaHouse, this is handled incorrectly and a multiplication is attempted with type(uint).max which will inadvertently revert.  
```solidity
function _withdrawFromTarget(uint256 withdrawAmount, address withdrawTarget, bytes memory swapData)
    internal
    override
{
    // Other option is to pass in the teahouse vault addresses in swapData
    for (uint256 i; i < s_teahouseVaults.length(); ++i) {
        address teahouseVaultAddr = s_teahouseVaults.at(i);
        bytes[] memory data = new bytes[](2);
        uint256 sharesAmt = Math.min(
            _convertToTeahouseShares(teahouseVaultAddr, withdrawAmount),
            IERC20(withdrawTarget).balanceOf(address(this))
        );
        ...
    }
}
```
```solidity
function _convertToTeahouseShares(address withdrawTarget, uint256 assetAmt) internal view returns (uint256) {
    ITeaVaultV3Pair teahouseVault = ITeaVaultV3Pair(withdrawTarget);
    address token = address(s_terms.asset);
    uint256 estimatedTokenValue = token == teahouseVault.assetToken0()
        ? teahouseVault.estimatedValueInToken0()
        : teahouseVault.estimatedValueInToken1();
    return assetAmt * IERC20(withdrawTarget).totalSupply() / estimatedTokenValue;
}
```
Calls to deactivate and liquidate will revert and can cause borrower to pay interest till their assets finish. Can be worked around by calling deactivate with 0 targets. It can also allow the withdrawer to enjoy the borrowed amount without interest even after the bond has been deactivated until all the withdrawers manually remove all their assets

## Recommendation
For the special case, directly assign sharesAmt to IERC20(withdrawTarget).balanceOf(address(this))
