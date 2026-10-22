# [H] `YaxisVaultAdapter.sol#withdraw

## Summary
Severity: High
Contest weight: 0.7436
Dataset id: 1254
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The actual token withdrawn from `vault.withdraw()` will most certainly less than the `_amount`, due to precision loss in `_tokensToShares()` and `vault.withdraw()`.

As a result, `IDetailedERC20(_token).safeTransfer(_recipient, _amount)` will revert due to insufficant balance.

Based on the simulation we ran, it will fail `99.99%` of the time unless the `pps == 1e18`.

```solidity
function withdraw(address _recipient, uint256 _amount) external override onlyAdmin {
    vault.withdraw(_tokensToShares(_amount));
    address _token = vault.getToken();
    IDetailedERC20(_token).safeTransfer(_recipient, _amount);
}

function withdraw(
    uint256 _shares
)
    public
    override
{
    uint256 _amount = (balance().mul(_shares)).div(IERC20(address(vaultToken)).totalSupply());
```

## Recommendation
```solidity
function withdraw(address _recipient, uint256 _amount) external override onlyAdmin {
    address _token = vault.getToken();
    uint256 beforeBalance = IDetailedERC20(_token).balanceOf(address(this));
    
    vault.withdraw(_tokensToShares(_amount));

    IDetailedERC20(_token).safeTransfer(
        _recipient,
        IDetailedERC20(_token).balanceOf(address(this)) - beforeBalance
    );
}
```
