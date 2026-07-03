### Title
Removed Allowed Token in `RsETHTokenWrapper` Freezes Deposited User Funds - (File: contracts/L2/RsETHTokenWrapper.sol)

### Summary
`RsETHTokenWrapper` allows users to deposit `altRsETH` tokens and receive `wrsETH` 1:1. The contract holds the deposited `altRsETH` as collateral. If the `TIMELOCK_ROLE` admin removes `altRsETH` from the `allowedTokens` registry via `removeAllowedToken`, the `_withdraw` function will permanently revert for that token, trapping all deposited `altRsETH` in the contract while users are left holding `wrsETH` they cannot redeem.

### Finding Description
The `_withdraw` internal function gates every withdrawal on the `allowedTokens` mapping:

```solidity
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
    ...
}
``` [1](#0-0) 

The `removeAllowedToken` function sets the flag to `false` with no precondition on

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L120-128)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, msg.sender, _to, _amount);
    }
```
