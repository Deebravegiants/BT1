### Title
Missing `nonReentrant` Modifier and CEI Violation in `RsETHTokenWrapper` Deposit/Withdraw Functions - (File: contracts/L2/RsETHTokenWrapper.sol)

---

### Summary

`RsETHTokenWrapper` does not inherit from any reentrancy guard and exposes four external state-modifying functions — `deposit`, `depositTo`, `withdraw`, and `withdrawTo` — without the `nonReentrant` modifier. The internal `_deposit` function additionally violates the Checks-Effects-Interactions (CEI) pattern by performing an external `safeTransferFrom` call before the `_mint` state update.

---

### Finding Description

`RsETHTokenWrapper` is an upgradeable ERC20 wrapper contract that allows users to exchange allowed altRsETH tokens 1:1 for `wrsETH`. The contract does not inherit `ReentrancyGuardUpgradeable` and none of its user-facing functions carry a `nonReentrant` modifier.

The four affected entry points are: [1](#0-0) 

They all delegate to `_deposit` or `_withdraw`:

**`_deposit` — CEI violation (external call before state update):** [2](#0-1) 

The sequence is:
1. `safeTransferFrom(msg.sender, address(this), _amount)` — **external call**
2. `_mint(_to, _amount)` — **state update after the external call**

This is the same pattern as the reported `startAuction` vulnerability: an external call is made to a third-party token contract before the contract's own state (`totalSupply`, balances) is updated.

**`_withdraw` — no `nonReentrant`, though CEI is followed:** [3](#0-2) 

`_burn` executes before `safeTransfer`, so `_withdraw` is CEI-compliant, but it still lacks `nonReentrant`, leaving the door open for cross-function reentrancy.

The `maxAmountToDepositBridgerAsset` view function, which is consumed by operator-facing swap functions, reads both `totalSupply()` and `balanceOf(address(this))`: [4](#0-3) 

During the window between `safeTransferFrom` completing and `_mint` executing in `_deposit`, `balanceOfAssetInWrapper` has already increased while `wrsETHSupply` has not, causing `maxAmountToDepositBridgerAsset` to transiently return a deflated (or zero) value. Any logic that reads this value during reentrancy would observe an inconsistent state.

---

### Impact Explanation

**Low.** The contract fails to follow the CEI pattern and lacks consistent reentrancy protection across all state-modifying public functions. If an allowed `asset` token implements a transfer callback (e.g., ERC-777 `tokensToSend`/`tokensReceived`, or a future token with hooks), a reentrant call during `_deposit` would observe stale `wrsETH` supply state. This could corrupt the invariant that `wrsETHSupply >= balanceOfAssetInWrapper`, which `maxAmountToDepositBridgerAsset` relies on, and could enable future upgrade paths or integrations to introduce exploitable reentrancy without any additional code change.

---

### Likelihood Explanation

**Low.** Currently, allowed tokens are added only by the `TIMELOCK_ROLE` admin and are expected to be standard ERC-20 altRsETH tokens without transfer callbacks. However, the absence of `nonReentrant` and the CEI violation mean the protection relies entirely on the properties of the allowed token set rather than on explicit code-level guards — a fragile assumption as the protocol evolves.

---

### Recommendation

1. Add `ReentrancyGuardUpgradeable` to `RsETHTokenWrapper`'s inheritance chain and call `__ReentrancyGuard_init()` in `initialize`.
2. Apply `nonReentrant` to `deposit`, `depositTo`, `withdraw`, and `withdrawTo`.
3. Reorder `_deposit` to follow CEI: call `_mint` before `safeTransferFrom`, or use a reentrancy guard as the primary protection.

```solidity
// CEI-compliant _deposit
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    _mint(_to, _amount);                                                    // effect first
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount); // interaction last
    emit Deposit(_asset, msg.sender, _to, _amount);
}
```

---

### Proof of Concept

Assume `altRsETH` is an ERC-777 token (or any token with a `tokensToSend` hook on the sender):

1. Attacker deploys `MaliciousContract` with a `tokensToSend` hook.
2. Attacker calls `RsETHTokenWrapper.deposit(altRsETH, amount)`.
3. Inside `_deposit`, `safeTransferFrom` triggers `MaliciousContract.tokensToSend`.
4. At this point `_mint` has **not** yet executed; `totalSupply()` is still the pre-call value.
5. `MaliciousContract.tokensToSend` calls `maxAmountToDepositBridgerAsset(altRsETH)`:
   - `balanceOfAssetInWrapper` has already increased (ERC-777 transfers before the hook in some implementations, or the hook fires mid-transfer).
   - `wrsETHSupply` has not increased yet.
   - The function returns `0` or an artificially low value, corrupting any dependent logic.
6. Control returns; `_mint` executes, restoring consistency — but the window of inconsistency was observable and callable by any external party. [1](#0-0) [2](#0-1) [4](#0-3)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L69-94)
```text
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

**File:** contracts/L2/RsETHTokenWrapper.sol (L99-110)
```text
    function maxAmountToDepositBridgerAsset(address _asset) public view returns (uint256) {
        if (!allowedTokens[_asset]) return 0;

        // get totalSupply of wrsETH minted
        uint256 wrsETHSupply = totalSupply();
        // balance of _asset with the contract
        uint256 balanceOfAssetInWrapper = ERC20Upgradeable(_asset).balanceOf(address(this));

        if (balanceOfAssetInWrapper > wrsETHSupply) return 0;

        return wrsETHSupply - balanceOfAssetInWrapper;
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
