### Title
`removeAllowedToken` Blocks Redemption of wrsETH Backed by Removed Token — (`contracts/L2/RsETHTokenWrapper.sol`)

---

### Summary

When `TIMELOCK_ROLE` removes a token via `removeAllowedToken`, any wrsETH minted against that token becomes unredeemable. The underlying collateral remains locked in the contract, but `_withdraw` unconditionally reverts for the removed token, breaking the 1:1 redemption invariant.

---

### Finding Description

`_withdraw` enforces that the requested asset is currently in the allowed list before burning wrsETH and transferring the asset: [1](#0-0) 

`removeAllowedToken` simply flips the mapping to `false` with no check on outstanding wrsETH supply backed by that token and no migration path: [2](#0-1) 

After removal, `allowedTokens[tokenA] == false`, so every call to `withdraw(tokenA, ...)` or `withdrawTo(tokenA, ...)` reverts with `TokenNotAllowed`. The tokenA balance remains in the contract but is inaccessible to wrsETH holders.

---

### Impact Explanation

Matches **Low — Contract fails to deliver promised returns, but doesn't lose value.**

- wrsETH holders who deposited tokenA cannot redeem their tokens; the 1:1 redemption promise is broken.
- The tokenA collateral is not lost — it sits in the contract — but it is inaccessible until/unless the token is re-added.
- If no other allowed token has sufficient balance, there is no alternative redemption path.

---

### Likelihood Explanation

`removeAllowedToken` is a routine governance operation (e.g., deprecating a bridged token variant, replacing it with a canonical one). It is realistic that this action is taken while users still hold wrsETH backed exclusively by the removed token. The TIMELOCK_ROLE is not acting maliciously; the contract simply has no guard against this state.

---

### Recommendation

Before setting `allowedTokens[_asset] = false`, verify that the contract holds zero balance of `_asset` (i.e., no outstanding wrsETH is backed by it), or provide a migration/emergency-withdrawal path that allows holders to redeem even after removal. For example:

```solidity
function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    // Ensure no wrsETH is backed by this asset
    require(ERC20Upgradeable(_asset).balanceOf(address(this)) == 0, "Outstanding balance");
    allowedTokens[_asset] = false;
    emit TokenRemoved(_asset);
}
```

Alternatively, allow withdrawal of a removed token in a separate emergency path that does not check `allowedTokens`.

---

### Proof of Concept

```solidity
// 1. tokenA is added and user deposits 100e18
wrapper.addAllowedToken(address(tokenA));          // TIMELOCK_ROLE
tokenA.approve(address(wrapper), 100e18);
wrapper.deposit(address(tokenA), 100e18);
// user now holds 100e18 wrsETH

// 2. TIMELOCK_ROLE removes tokenA (legitimate governance action)
wrapper.removeAllowedToken(address(tokenA));       // TIMELOCK_ROLE

// 3. User tries to redeem — reverts with TokenNotAllowed
vm.expectRevert(RsETHTokenWrapper.TokenNotAllowed.selector);
wrapper.withdraw(address(tokenA), 100e18);

// 4. No other allowed token exists with sufficient balance
// => 100e18 wrsETH is permanently unredeemable until tokenA is re-added
```

The revert at step 3 is caused by line 121 of `_withdraw`: [3](#0-2)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L120-122)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

```

**File:** contracts/L2/RsETHTokenWrapper.sol (L180-185)
```text
    function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        allowedTokens[_asset] = false;
        emit TokenRemoved(_asset);
    }
```
