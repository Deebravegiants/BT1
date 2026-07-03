### Title
`removeAllowedToken` Removes Token Without Checking Active Deposits, Permanently Freezing User Funds - (File: contracts/L2/RsETHTokenWrapper.sol)

---

### Summary

`RsETHTokenWrapper.removeAllowedToken` sets `allowedTokens[_asset] = false` with no check on whether the contract currently holds a balance of that token. Because `_withdraw` gates on `allowedTokens[_asset]`, any user who deposited that alt-rsETH token and received wrsETH is permanently unable to redeem their underlying tokens after removal.

---

### Finding Description

`RsETHTokenWrapper` is a 1:1 lockbox: users call `deposit`/`depositTo` to lock an allowed alt-rsETH token and receive wrsETH; they call `withdraw`/`withdrawTo` to burn wrsETH and recover the underlying token.

The `removeAllowedToken` function:

```solidity
// contracts/L2/RsETHTokenWrapper.sol:180-185
function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();

    allowedTokens[_asset] = false;
    emit TokenRemoved(_asset);
}
```

performs no balance check before disabling the token. [1](#0-0) 

The withdrawal path unconditionally reverts for any non-allowed token:

```solidity
// contracts/L2/RsETHTokenWrapper.sol:120-128
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
    emit Withdraw(_asset, msg.sender, _to, _amount);
}
``` [2](#0-1) 

Once `allowedTokens[_asset]` is `false`, every call to `withdraw`, `withdrawTo` for that asset reverts. The underlying alt-rsETH tokens remain locked in the contract with no recovery path for users.

Contrast this with every pool contract in the same repository, which explicitly guards removal with a balance check:

```solidity
// contracts/pools/RSETHPoolV3.sol:562
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
``` [3](#0-2) 

And `LRTConfig.removeSupportedAsset` checks total deposits before removal:

```solidity
// contracts/LRTConfig.sol:82-84
if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
    revert CannotRemoveAssetWithDeposits(asset);
}
``` [4](#0-3) 

`RsETHTokenWrapper.removeAllowedToken` is the only removal function in the protocol that lacks this guard. [5](#0-4) 

---

### Impact Explanation

Any alt-rsETH tokens deposited into the wrapper before the removal call become permanently inaccessible to users. The wrsETH they hold is backed by those locked tokens, but they cannot burn it to recover the underlying asset. This constitutes a **permanent freezing of user funds** (Critical) or at minimum a **temporary freeze** (Medium) if the admin re-adds the token — but there is no on-chain guarantee of re-addition, and the protocol provides no alternative recovery path.

---

### Likelihood Explanation

The TIMELOCK_ROLE is a governance/admin role, not an attacker. However, the vulnerability class here is the same as the original report: a legitimate administrative action (deprecating an old alt-rsETH token variant) executed without the protocol enforcing a safety check. This is a realistic operational scenario — the protocol already supports multiple allowed tokens via `addAllowedToken`/`removeAllowedToken`, and token deprecation is an expected lifecycle event. The missing balance check means the action can silently freeze user funds.

---

### Recommendation

Before setting `allowedTokens[_asset] = false`, verify that the contract holds no balance of that token:

```solidity
function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    if (ERC20Upgradeable(_asset).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

    allowedTokens[_asset] = false;
    emit TokenRemoved(_asset);
}
```

This mirrors the guard already present in `RSETHPoolV3.removeSupportedToken` and all other pool contracts in the repository. [3](#0-2) 

---

### Proof of Concept

1. TIMELOCK_ROLE calls `addAllowedToken(altRsETH)` — `allowedTokens[altRsETH] = true`.
2. Alice calls `deposit(altRsETH, 100e18)` — 100 altRsETH locked in wrapper, Alice receives 100 wrsETH.
3. TIMELOCK_ROLE calls `removeAllowedToken(altRsETH)` — `allowedTokens[altRsETH] = false`. No balance check; succeeds despite 100 altRsETH sitting in the contract.
4. Alice calls `withdraw(altRsETH, 100e18)` — `_withdraw` hits `if (!allowedTokens[_asset]) revert TokenNotAllowed()` and reverts.
5. Alice's 100 altRsETH tokens are permanently locked in `RsETHTokenWrapper` with no on-chain recovery path. [2](#0-1) [1](#0-0)

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

**File:** contracts/pools/RSETHPoolV3.sol (L559-567)
```text
    function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

        delete supportedTokenOracle[token];
        supportedTokenList[tokenIndex] = supportedTokenList[supportedTokenList.length - 1];
        supportedTokenList.pop();
        emit RemovedSupportedToken(token);
```

**File:** contracts/LRTConfig.sol (L80-84)
```text
        address depositPool = getContract(LRTConstants.LRT_DEPOSIT_POOL);

        if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
            revert CannotRemoveAssetWithDeposits(asset);
        }
```
