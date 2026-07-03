### Title
Irreversible `removeAllowedToken` With No Balance Check Permanently Freezes All User Funds — (`contracts/agETH/AGETHTokenWrapper.sol`)

---

### Summary

`AGETHTokenWrapper` exposes a `removeAllowedToken` function callable by `DEFAULT_ADMIN_ROLE` that sets `allowedTokens[_asset] = false` with no balance check and no on-chain recovery path. Because `_withdraw` gates every redemption on `allowedTokens[_asset]`, removing the sole allowed token while the contract holds a non-zero balance permanently traps all deposited altAgETH with no way to recover it.

---

### Finding Description

`removeAllowedToken` in `AGETHTokenWrapper` is a one-way door:

```solidity
// contracts/agETH/AGETHTokenWrapper.sol line 157-160
function removeAllowedToken(address _asset) external onlyRole(DEFAULT_ADMIN_ROLE) {
    allowedTokens[_asset] = false;
    emit TokenRemoved(_asset);
}
``` [1](#0-0) 

There is no balance check before removal, and the contract explicitly blocks adding tokens back — the comment at line 153 reads *"Don't allow to add other tokens at the moment"* and there is no `addAllowedToken` function anywhere in the contract. [2](#0-1) 

Every redemption path (`withdraw`, `withdrawTo`) routes through `_withdraw`, which hard-reverts on a non-allowed token:

```solidity
// contracts/agETH/AGETHTokenWrapper.sol line 112
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    ...
}
``` [3](#0-2) 

This is a direct design asymmetry with `RsETHTokenWrapper`, which protects against this exact scenario by (a) gating removal behind `TIMELOCK_ROLE` instead of the immediate `DEFAULT_ADMIN_ROLE`, (b) checking `if (!allowedTokens[_asset]) revert TokenNotAllowed()` before removal, and (c) providing a symmetric `addAllowedToken` via `TIMELOCK_ROLE` for recovery: [4](#0-3) 

---

### Impact Explanation

Once `removeAllowedToken(altAgETH)` is called:

- Every call to `withdraw(altAgETH, N)` or `withdrawTo(altAgETH, _, N)` reverts with `TokenNotAllowed`.
- The altAgETH balance remains locked in the contract forever — `altAgETH.balanceOf(wrapper) == N` with no on-chain path to recover it.
- Wrapper agETH tokens held by users become permanently non-redeemable, destroying their value.
- There is no upgrade path within the contract itself (no `addAllowedToken`), so recovery would require a proxy upgrade — an out-of-band, governance-dependent action not guaranteed to exist.

**Impact: Critical — Permanent freezing of funds.**

---

### Likelihood Explanation

The trigger is a single `DEFAULT_ADMIN_ROLE` transaction. This does not require a malicious admin; it can happen:

- During a planned token migration where the admin removes the old altAgETH address expecting to add a new one (as is possible in `RsETHTokenWrapper`).
- By operational mistake, given the function exists and is callable without any warning or balance guard.

The asymmetry with `RsETHTokenWrapper` strongly suggests this is an unintentional omission rather than a deliberate design choice.

---

### Recommendation

1. Add an `addAllowedToken` function (gated behind `TIMELOCK_ROLE` or equivalent time-delayed role, mirroring `RsETHTokenWrapper`).
2. Add a balance check in `removeAllowedToken` to prevent removal while the contract holds a non-zero balance of the asset:
   ```solidity
   require(ERC20Upgradeable(_asset).balanceOf(address(this)) == 0, "NonZeroBalance");
   ```
3. Gate `removeAllowedToken` behind `TIMELOCK_ROLE` instead of `DEFAULT_ADMIN_ROLE` to introduce a time delay for user reaction.

---

### Proof of Concept

```solidity
// Local fork / unit test — no mainnet interaction
function testPermanentFreeze() public {
    // 1. Deploy wrapper with altAgETH as the sole allowed token
    AGETHTokenWrapper wrapper = new AGETHTokenWrapper();
    wrapper.initialize(admin, manager, address(altAgETH));

    // 2. User deposits N altAgETH, receives N wrapper tokens
    vm.startPrank(user);
    altAgETH.approve(address(wrapper), N);
    wrapper.deposit(address(altAgETH), N);
    vm.stopPrank();

    assertEq(wrapper.balanceOf(user), N);
    assertEq(altAgETH.balanceOf(address(wrapper)), N);

    // 3. Admin removes the only allowed token (no balance check, no recovery path)
    vm.prank(admin);
    wrapper.removeAllowedToken(address(altAgETH));

    // 4. User can never withdraw — permanently frozen
    vm.prank(user);
    vm.expectRevert(AGETHTokenWrapper.TokenNotAllowed.selector);
    wrapper.withdraw(address(altAgETH), N);

    // altAgETH is permanently locked in the wrapper
    assertEq(altAgETH.balanceOf(address(wrapper)), N); // never moves
}
```

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

**File:** contracts/agETH/AGETHTokenWrapper.sol (L153-154)
```text
    /// Dont' allow to add other tokens at the moment. Only allow the altAgETH token as set in the initialize function

```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L157-160)
```text
    function removeAllowedToken(address _asset) external onlyRole(DEFAULT_ADMIN_ROLE) {
        allowedTokens[_asset] = false;
        emit TokenRemoved(_asset);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L174-185)
```text
    function addAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        _addAllowedToken(_asset);
    }

    /// @dev Remove a token from the allowed tokens list
    /// @param _asset The address of the token to remove
    function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        allowedTokens[_asset] = false;
        emit TokenRemoved(_asset);
    }
```
