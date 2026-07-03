### Title
`removeAllowedToken` Permanently Blocks wrsETH Redemption for Removed Token — (`contracts/L2/RsETHTokenWrapper.sol`)

### Summary

When `TIMELOCK_ROLE` removes a token via `removeAllowedToken`, the `_withdraw` guard immediately rejects any redemption attempt for that token. If users hold wrsETH backed exclusively by the removed token and no other allowed token has sufficient balance, their wrsETH becomes permanently unredeemable — the contract retains the underlying tokens but cannot return them.

### Finding Description

`_withdraw` enforces an `allowedTokens` check before burning wrsETH and transferring the underlying asset: [1](#0-0) 

`removeAllowedToken` sets `allowedTokens[_asset] = false` with no grace period, no balance check, and no migration path: [2](#0-1) 

After removal, `_withdraw` hits line 121 and reverts with `TokenNotAllowed` for every call specifying the removed token, even though the contract still holds the full balance of that token. The underlying tokens are locked in the contract with no withdrawal path. [3](#0-2) 

### Impact Explanation

Users holding wrsETH minted from the removed token cannot redeem 1:1 as the contract promises. The underlying tokens remain in the contract (no value is lost), but the redemption invariant is broken. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**.

### Likelihood Explanation

`removeAllowedToken` is a legitimate governance action (e.g., deprecating a bridged token variant). No malicious intent is required — a routine token migration without a prior withdrawal window is sufficient to trigger the freeze. The `TIMELOCK_ROLE` is a distinct role from `DEFAULT_ADMIN_ROLE`, making this a realistic operational scenario.

### Recommendation

Before setting `allowedTokens[_asset] = false`, verify that the contract holds zero balance of the asset (i.e., all deposits have already been withdrawn or migrated):

```solidity
function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    if (ERC20Upgradeable(_asset).balanceOf(address(this)) != 0) revert TokenStillHasBalance();
    allowedTokens[_asset] = false;
    emit TokenRemoved(_asset);
}
```

Alternatively, allow withdrawal of removed tokens for a defined grace period, or add an emergency-rescue function restricted to `DEFAULT_ADMIN_ROLE` that can return stranded tokens to users.

### Proof of Concept

```solidity
// 1. tokenA is added and user deposits 100e18
wrapper.addAllowedToken(tokenA);                        // TIMELOCK_ROLE
tokenA.approve(address(wrapper), 100e18);
wrapper.deposit(tokenA, 100e18);                        // user receives 100e18 wrsETH

// 2. TIMELOCK_ROLE removes tokenA (legitimate governance action)
wrapper.removeAllowedToken(tokenA);                     // TIMELOCK_ROLE

// 3. User tries to redeem — reverts with TokenNotAllowed
vm.expectRevert(RsETHTokenWrapper.TokenNotAllowed.selector);
wrapper.withdraw(tokenA, 100e18);

// 4. No other allowed token exists with sufficient balance
// → 100e18 wrsETH is permanently unredeemable
// → 100e18 tokenA is permanently locked in the contract
assertEq(tokenA.balanceOf(address(wrapper)), 100e18);   // tokens still there
assertEq(wrapper.balanceOf(user), 100e18);              // wrsETH still held
```

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
