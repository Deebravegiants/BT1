### Title
`removeAllowedToken` Does Not Check Residual Balance Before Disabling Withdrawal Path — Permanent Freezing of User Funds - (File: contracts/L2/RsETHTokenWrapper.sol)

---

### Summary

`RsETHTokenWrapper.removeAllowedToken` sets `allowedTokens[_asset] = false` without verifying that the contract holds zero balance of that token. Because `_withdraw` gates every user redemption on `allowedTokens[_asset]`, removing a token while the contract still holds it permanently blocks all wrsETH holders from redeeming their underlying collateral.

---

### Finding Description

`RsETHTokenWrapper` is a 1:1 lockbox: users deposit an allowed altRsETH token and receive wrsETH; they redeem wrsETH to recover the underlying token. The contract's entire withdrawal path is gated on the `allowedTokens` mapping:

```solidity
// contracts/L2/RsETHTokenWrapper.sol  line 121
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
    emit Withdraw(_asset, msg.sender, _to, _amount);
}
```

The admin function that removes a token performs no balance check before flipping the flag:

```solidity
// contracts/L2/RsETHTokenWrapper.sol  lines 180-185
function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    allowedTokens[_asset] = false;
    emit TokenRemoved(_asset);
}
```

Contrast this with every pool contract (`RSETHPoolV3`, `RSETHPool`, `RSETHPoolNoWrapper`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) and `LRTConfig.removeSupportedAsset`, all of which enforce a zero-balance invariant before removing a token. `RsETHTokenWrapper` is the only removal path that skips this check.

The same defect exists in `AGETHTokenWrapper.removeAllowedToken` (contracts/agETH/AGETHTokenWrapper.sol line 157), which does not even verify the token is currently allowed before clearing the flag. [1](#0-0) [2](#0-1) [3](#0-2) 

---

### Impact Explanation

After `removeAllowedToken(_asset)` is called while `ERC20Upgradeable(_asset).balanceOf(address(this)) > 0`:

- Every call to `withdraw` / `withdrawTo` for `_asset` reverts with `TokenNotAllowed`.
- The underlying altRsETH tokens remain locked in the contract with no user-accessible exit path.
- wrsETH holders who deposited the removed token hold tokens that are no longer redeemable for their collateral.
- There is no emergency user-withdrawal function; recovery requires the TIMELOCK_ROLE to re-add the token via `addAllowedToken`, which is a separate governance action that may not happen.

**Impact: Medium — Temporary (potentially permanent) freezing of user funds.** [4](#0-3) 

---

### Likelihood Explanation

The TIMELOCK_ROLE is expected to perform routine token lifecycle management (e.g., deprecating a bridged altRsETH variant when a canonical bridge is upgraded). The missing balance check is a silent omission — the transaction succeeds, emits `TokenRemoved`, and gives no indication that user funds are now frozen. The likelihood of this occurring during a legitimate token migration is realistic.

---

### Recommendation

Add a zero-balance guard in `removeAllowedToken`, mirroring the pattern used in every pool contract:

```solidity
function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    if (ERC20Upgradeable(_asset).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
    allowedTokens[_asset] = false;
    emit TokenRemoved(_asset);
}
```

Apply the same fix to `AGETHTokenWrapper.removeAllowedToken`. Document the required state-machine invariant: a token may only be removed after all depositors have withdrawn and the contract balance is zero. [5](#0-4) 

---

### Proof of Concept

1. User A calls `deposit(altRsETH, 100e18)` → receives 100 wrsETH. Contract holds 100 altRsETH.
2. TIMELOCK_ROLE calls `removeAllowedToken(altRsETH)` (e.g., to migrate to a new bridge). Transaction succeeds; `allowedTokens[altRsETH] = false`.
3. User A calls `withdraw(altRsETH, 100e18)` → reverts with `TokenNotAllowed`.
4. User A's 100 wrsETH is now unbacked by any accessible collateral. The 100 altRsETH sits permanently in the contract unless TIMELOCK_ROLE re-adds the token. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L66-94)
```text
    /// @dev Deposit altRsETH for wrsETH
    /// @param asset The address of the token to deposit
    ///@param _amount The amount of tokens to deposit
    function deposit(address asset, uint256 _amount) external {
        _deposit(asset, msg.sender, _amount);
    }

    /// @dev Deposit altRsETH for wrsETH to a user
    /// @param asset The address of the token to deposit
    /// @param _to The user to send the XERC20 to
    /// @param _amount The amount of tokens to deposit
    function depositTo(address asset, address _to, uint256 _amount) external {
        _deposit(asset, _to, _amount);
    }

    /// @dev Withdraw altRseth tokens from wrsETH
    /// @param asset The address of the token to withdraw
    /// @param _amount The amount of tokens to withdraw
    function withdraw(address asset, uint256 _amount) external {
        _withdraw(asset, msg.sender, _amount);
    }

    /// @dev Withdraw altRsETH tokens from wrsETH to a user
    /// @param asset The address of the token to withdraw
    /// @param _to The user to withdraw to
    /// @param _amount The amount of tokens to withdraw
    function withdrawTo(address asset, address _to, uint256 _amount) external {
        _withdraw(asset, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L120-128)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, msg.sender, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L134-141)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, msg.sender, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L143-151)
```text
    /// @notice Internal function to add a token to the allowed tokens list
    /// @param _asset The address of the token to add
    function _addAllowedToken(address _asset) internal {
        UtilLib.checkNonZeroAddress(_asset);
        if (allowedTokens[_asset]) revert TokenAlreadyAllowed();

        allowedTokens[_asset] = true;
        emit TokenAdded(_asset);
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

**File:** contracts/agETH/AGETHTokenWrapper.sol (L155-160)
```text
    /// @dev Remove a token from the allowed tokens list
    /// @param _asset The address of the token to remove
    function removeAllowedToken(address _asset) external onlyRole(DEFAULT_ADMIN_ROLE) {
        allowedTokens[_asset] = false;
        emit TokenRemoved(_asset);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L769-779)
```text
    function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

        delete supportedTokenOracle[token];
        delete tokenBridge[token];
        supportedTokenList[tokenIndex] = supportedTokenList[supportedTokenList.length - 1];
        supportedTokenList.pop();
        emit RemovedSupportedToken(token);
    }
```
