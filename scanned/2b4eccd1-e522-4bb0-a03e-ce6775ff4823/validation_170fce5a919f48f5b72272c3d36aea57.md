### Title
`removeAllowedToken` Removes Deposited Asset Without Balance Validation, Permanently Freezing User Funds - (File: contracts/agETH/AGETHTokenWrapper.sol)

### Summary
`AGETHTokenWrapper.removeAllowedToken` sets `allowedTokens[_asset] = false` with no check on the contract's current balance of that asset. Because `_withdraw` gates on `allowedTokens[_asset]`, any altAgETH tokens already deposited by users become permanently unrecoverable the moment the token is removed.

### Finding Description
`AGETHTokenWrapper` is a 1:1 lockbox wrapper: users call `deposit`/`depositTo`, which transfers their altAgETH tokens into the contract and mints an equal amount of canonical agETH. To redeem, users call `withdraw`/`withdrawTo`, which burns their agETH and transfers the underlying altAgETH back.

The `_withdraw` internal function enforces:

```solidity
// contracts/agETH/AGETHTokenWrapper.sol L112
if (!allowedTokens[_asset]) revert TokenNotAllowed();
```

The admin-callable removal function performs no balance check before disabling the token:

```solidity
// contracts/agETH/AGETHTokenWrapper.sol L157-160
function removeAllowedToken(address _asset) external onlyRole(DEFAULT_ADMIN_ROLE) {
    allowedTokens[_asset] = false;
    emit TokenRemoved(_asset);
}
```

Once `allowedTokens[_asset]` is `false`, every call to `withdraw` or `withdrawTo` for that asset reverts unconditionally. There is no emergency-rescue path, no alternative withdrawal route, and no way for users to recover their deposited tokens without re-enabling the asset (which itself requires admin action).

By contrast, the analogous function in `RsETHTokenWrapper.removeAllowedToken` (line 180) at least verifies the token is currently allowed before acting, and the L2 pool contracts (`RSETHPoolV3.removeSupportedToken` line 562, `RSETHPool.removeSupportedToken` line 663) explicitly revert with `TokenBalanceNotZero` if the contract still holds any balance. `AGETHTokenWrapper` has neither guard. [1](#0-0) [2](#0-1) [3](#0-2) 

### Impact Explanation
Any altAgETH tokens held in `AGETHTokenWrapper` at the time `removeAllowedToken` is called are permanently frozen. Users who deposited those tokens hold agETH that can no longer be redeemed for the underlying asset. Because the contract holds the tokens directly (not in an external protocol), there is no secondary recovery mechanism. This constitutes **permanent freezing of user funds** (Critical). [4](#0-3) 

### Likelihood Explanation
The function requires `DEFAULT_ADMIN_ROLE`. The realistic scenario is an admin legitimately deprecating an altAgETH variant (e.g., a bridged token being replaced by a canonical one) without first verifying that the contract's balance of that token is zero. Because there is no on-chain guard to prevent this, the mistake is operationally plausible and requires no attacker involvement. The impact is irreversible once executed. [2](#0-1) 

### Recommendation
Add a balance guard to `removeAllowedToken`, mirroring the pattern already used in the L2 pool contracts:

```solidity
function removeAllowedToken(address _asset) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    if (ERC20Upgradeable(_asset).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
    allowedTokens[_asset] = false;
    emit TokenRemoved(_asset);
}
```

Apply the same fix to `RsETHTokenWrapper.removeAllowedToken` (line 180), which also lacks a balance check. [5](#0-4) 

### Proof of Concept
1. User calls `AGETHTokenWrapper.deposit(altAgETH, 100e18)`. The contract receives 100 altAgETH and mints 100 agETH to the user.
2. Admin calls `AGETHTokenWrapper.removeAllowedToken(altAgETH)`. `allowedTokens[altAgETH]` is set to `false`. No balance check is performed; the 100 altAgETH remain in the contract.
3. User calls `AGETHTokenWrapper.withdraw(altAgETH, 100e18)`. Execution reaches `_withdraw`, which evaluates `if (!allowedTokens[altAgETH]) revert TokenNotAllowed()` and reverts.
4. The 100 altAgETH are permanently locked. The user's agETH is now unbacked and unredeemable for the underlying asset. [6](#0-5) [1](#0-0)

### Citations

**File:** contracts/agETH/AGETHTokenWrapper.sol (L60-62)
```text
    function deposit(address asset, uint256 _amount) external {
        _deposit(asset, msg.sender, _amount);
    }
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L111-119)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, _to, _amount);
    }
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L125-131)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, _to, _amount);
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L157-160)
```text
    function removeAllowedToken(address _asset) external onlyRole(DEFAULT_ADMIN_ROLE) {
        allowedTokens[_asset] = false;
        emit TokenRemoved(_asset);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L559-568)
```text
    function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

        delete supportedTokenOracle[token];
        supportedTokenList[tokenIndex] = supportedTokenList[supportedTokenList.length - 1];
        supportedTokenList.pop();
        emit RemovedSupportedToken(token);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L178-185)
```text
    /// @dev Remove a token from the allowed tokens list
    /// @param _asset The address of the token to remove
    function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        allowedTokens[_asset] = false;
        emit TokenRemoved(_asset);
    }
```
