# [M] TeavaultPairHelper is called instead of

## Summary
Severity: Medium
Contest weight: 0.3928
Dataset id: 22618
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
TeavaultPairHelper is called instead of TeaVaultV3Pair to fetch balance  
When withdrawing from Teahouse vaults, the balances are attempted to be fetched from the withdrawTarget which would be the address of the ITeaVaultV3PairHelper contract and not the vault  
```solidity
function _withdrawFromTarget(uint256 withdrawAmount, address withdrawTarget, bytes memory swapData)
    internal
    override
{
    // withdrawTarget is the helperContract
    uint256 sharesAmt = Math.min(
        _convertToTeahouseShares(teahouseVaultAddr, withdrawAmount),
        IERC20(withdrawTarget).balanceOf(address(this))
    );
}
```
This will cause the _withdrawFromTarget function call to fail and user's won't be able to withdraw from Teahouse  
Assets cannot be withdrawn from Teahouse

## Recommendation
Use TeahouseVaultAddress instead
