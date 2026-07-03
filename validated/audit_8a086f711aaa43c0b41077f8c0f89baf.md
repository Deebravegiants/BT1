Let me check the `AGETHTokenWrapper.sol` and `LRTConverter.sol` for additional context before finalizing.

### Title
`removeAllowedToken` Freezes User Deposits Due to Asymmetric Token Validation Between Deposit and Withdraw — (File: contracts/agETH/AGETHTokenWrapper.sol and contracts/L2/RsETHTokenWrapper.sol)

---

### Summary

Both `AGETHTokenWrapper` and `RsETHTokenWrapper` accept any `allowedToken` at deposit time, but the `_withdraw` path enforces the same `allowedTokens[_asset]` check at withdrawal time. The `removeAllowedToken` function removes a token without verifying that the contract holds no user deposits of that token. Once removed, users who deposited that token cannot withdraw it. In `AGETHTokenWrapper` the freeze is **permanent** because no `addAllowedToken` function exists; in `RsETHTokenWrapper` it is at minimum temporary.

---

### Finding Description

**Deposit path — accepts any currently-allowed token:**

`AGETHTokenWrapper._deposit` (line 125–131):
```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
    _mint(_to, _amount);
    ...
}
``` [1](#0-0) 

**Withdraw path — enforces the same `allowedTokens` check at withdrawal time:**

`AGETHTokenWrapper._withdraw` (line 111–119):
```solidity
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
    ...
}
``` [2](#0-1) 

**`removeAllowedToken` — no balance guard, no recovery path:**

```solidity
function removeAllowedToken(address _asset) external onlyRole(DEFAULT_ADMIN_ROLE) {
    allowedTokens[_asset] = false;
    emit TokenRemoved(_asset);
}
``` [3](#0-2) 

The comment at line 153 explicitly states: *"Don't allow to add other tokens at the moment."* There is no `addAllowedToken` function in `AGETHTokenWrapper`, so once a token is removed it **cannot be re-added**. [4](#0-3) 

The identical structural pattern exists in `RsETHTokenWrapper`: [5](#0-4) [6](#0-5) 

`RsETHTokenWrapper` does have `addAllowedToken` (callable by `TIMELOCK_ROLE`), so its freeze is recoverable in principle — but only if the admin acts. [7](#0-6) 

---

### Impact Explanation

**`AGETHTokenWrapper` — Critical / Permanent freezing of funds.**
Any user who deposited altAgETH token A and holds wrapped agETH cannot redeem token A after it is removed. Because no `addAllowedToken` exists, the contract's balance of token A is permanently inaccessible to users. The wrapped agETH they hold becomes unbacked and unwithdrawable.

**`RsETHTokenWrapper` — Medium / Temporary freezing of funds.**
The same freeze occurs, but `TIMELOCK_ROLE` can call `addAllowedToken` to restore the token. Until that happens, all user deposits of the removed token are locked.

---

### Likelihood Explanation

The `removeAllowedToken` function is a legitimate operational function (e.g., deprecating a bridged altRsETH/altAgETH variant from a sunset chain). No malicious intent is required. The admin only needs to call it once — without first verifying the contract's token balance is zero — to trigger the freeze. The likelihood is **Low** in isolation but the consequence is severe and irreversible for `AGETHTokenWrapper`.

---

### Recommendation

1. **Guard `removeAllowedToken` with a balance check:**
   ```solidity
   function removeAllowedToken(address _asset) external onlyRole(...) {
       require(ERC20Upgradeable(_asset).balanceOf(address(this)) == 0,
               "Cannot remove: user deposits exist");
       allowedTokens[_asset] = false;
       emit TokenRemoved(_asset);
   }
   ```
2. **For `AGETHTokenWrapper`:** Add an `addAllowedToken` function (gated by admin/timelock) so that a mistakenly removed token can be re-enabled, providing a recovery path.
3. **Alternatively:** In `_withdraw`, allow withdrawal of tokens that are no longer in `allowedTokens` if the user's wrsETH/agETH balance is sufficient (only block new deposits for removed tokens).

---

### Proof of Concept

**`AGETHTokenWrapper` — permanent freeze:**

1. User calls `deposit(tokenA, 1000e18)` → receives 1000 agETH. Contract holds 1000 tokenA.
2. Admin calls `removeAllowedToken(tokenA)` (legitimate deprecation action).
3. User calls `withdraw(tokenA, 1000e18)` → reverts: `TokenNotAllowed`.
4. No `addAllowedToken` exists → user's 1000 agETH is permanently unbacked and unwithdrawable.
5. The 1000 tokenA sitting in the contract is inaccessible to any user.

**`RsETHTokenWrapper` — same path, temporary until admin re-adds:**

1. User calls `deposit(tokenA, 1000e18)` → receives 1000 wrsETH.
2. `TIMELOCK_ROLE` calls `removeAllowedToken(tokenA)`.
3. User calls `withdraw(tokenA, 1000e18)` → reverts: `TokenNotAllowed`.
4. Funds remain frozen until `TIMELOCK_ROLE` calls `addAllowedToken(tokenA)`.

### Citations

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

**File:** contracts/agETH/AGETHTokenWrapper.sol (L153-160)
```text
    /// Dont' allow to add other tokens at the moment. Only allow the altAgETH token as set in the initialize function

    /// @dev Remove a token from the allowed tokens list
    /// @param _asset The address of the token to remove
    function removeAllowedToken(address _asset) external onlyRole(DEFAULT_ADMIN_ROLE) {
        allowedTokens[_asset] = false;
        emit TokenRemoved(_asset);
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

**File:** contracts/L2/RsETHTokenWrapper.sol (L174-176)
```text
    function addAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        _addAllowedToken(_asset);
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
