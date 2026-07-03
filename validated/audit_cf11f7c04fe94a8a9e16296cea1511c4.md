### Title
`removeAllowedToken` Without Balance Check Permanently Freezes User Funds in Wrapper - (File: contracts/L2/RsETHTokenWrapper.sol)

### Summary
`RsETHTokenWrapper.removeAllowedToken` sets `allowedTokens[_asset] = false` with no check on whether the wrapper still holds a balance of that asset. Because `_withdraw` hard-reverts on any removed token, users who deposited an `altRsETH` variant before removal can never redeem their `wrsETH` for the underlying asset, permanently locking those tokens in the contract.

### Finding Description
`RsETHTokenWrapper` is the L2 lockbox that accepts one or more "alternative rsETH" tokens (bridged variants) in exchange for `wrsETH` on a 1:1 basis. The contract explicitly supports multiple allowed tokens via `addAllowedToken` and `reinitialize`.

The withdrawal path hard-gates on the `allowedTokens` mapping:

```solidity
// contracts/L2/RsETHTokenWrapper.sol:120-128
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();   // ← hard gate
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
    emit Withdraw(_asset, msg.sender, _to, _amount);
}
```

The removal function performs no balance check before disabling the token:

```solidity
// contracts/L2/RsETHTokenWrapper.sol:180-185
function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    allowedTokens[_asset] = false;          // ← no balance check
    emit TokenRemoved(_asset);
}
```

Compare this with every pool contract in the same codebase, which correctly guards removal with a balance check:

```solidity
// contracts/pools/RSETHPoolV3.sol:562
if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
```

`RsETHTokenWrapper` has no equivalent guard.

### Impact Explanation
Any `altRsETH` tokens deposited by users before `removeAllowedToken` is called become permanently unrecoverable. The wrapper holds the physical tokens, but the only exit path (`withdraw` / `withdrawTo`) reverts unconditionally for the removed asset. There is no emergency-rescue or migration function. Users holding `wrsETH` that was minted against the removed token cannot redeem it for any asset, constituting a **permanent freeze of user funds** (Critical).

### Likelihood Explanation
The protocol has already exercised the multi-token path: `reinitialize` was added specifically to register a second `altRsETH` token. Removing a deprecated bridge variant (e.g., after migrating to a new bridge) is a routine operational action. The TIMELOCK_ROLE holder has no on-chain signal that the wrapper still holds a balance of the token being removed, making an inadvertent freeze highly plausible during any bridge migration or token upgrade.

### Recommendation
Mirror the guard used in every pool contract: revert if the wrapper's balance of the asset is non-zero before disabling it.

```solidity
function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    if (ERC20Upgradeable(_asset).balanceOf(address(this)) != 0)
        revert TokenBalanceNotZero();   // add this error
    allowedTokens[_asset] = false;
    emit TokenRemoved(_asset);
}
```

Alternatively, provide a migration path that lets users swap the removed token for a still-allowed token before removal takes effect.

### Proof of Concept
1. Alice calls `deposit(altRsETH_A, 100e18)` on `RsETHTokenWrapper`. She receives 100 `wrsETH`; the wrapper now holds 100 `altRsETH_A`.
2. TIMELOCK_ROLE calls `removeAllowedToken(altRsETH_A)` — succeeds because there is no balance check.
3. Alice calls `withdraw(altRsETH_A, 100e18)`. The call reverts at `if (!allowedTokens[_asset]) revert TokenNotAllowed()`.
4. Alice's 100 `altRsETH_A` are permanently locked inside the wrapper. Her `wrsETH` is now unbacked and unredeemable for the asset she deposited.

**Root cause lines:** [1](#0-0) [2](#0-1) 

**Contrast — pool contracts do check balance before removal:** [3](#0-2)

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

**File:** contracts/L2/RsETHTokenWrapper.sol (L180-185)
```text
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
