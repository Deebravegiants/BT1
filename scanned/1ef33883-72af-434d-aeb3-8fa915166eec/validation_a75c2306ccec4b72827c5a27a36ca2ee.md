The vulnerability is real and concrete. Here is the full analysis:

---

### Title
Missing Balance Guard in `removeAllowedToken` Enables Permanent Freezing of All wrsETH Holders' Funds — (`contracts/L2/RsETHTokenWrapper.sol`)

---

### Summary

`RsETHTokenWrapper.removeAllowedToken` sets `allowedTokens[_asset] = false` with no check on the contract's token balance or outstanding wrsETH supply. Since `_withdraw` hard-gates on `allowedTokens[_asset] == true` and there is no alternative redemption path, removing the only allowed token while wrsETH is in circulation permanently bricks all holders.

---

### Finding Description

`removeAllowedToken` contains only a single guard — that the token is currently allowed — before disabling it: [1](#0-0) 

There is no check for:
- The contract's balance of `_asset` (i.e., collateral already deposited)
- The outstanding `totalSupply()` of wrsETH

Every withdrawal path funnels through `_withdraw`, which unconditionally reverts if the token is not allowed: [2](#0-1) 

The `mint` function compounds this by minting wrsETH without requiring any underlying deposit, meaning wrsETH supply can exist without a corresponding `deposit()` call that would at least require the token to be allowed at mint time: [3](#0-2) 

There is no emergency exit, no `rescueTokens`, no alternative burn path. Once `allowedTokens[altRsETH] = false`, all wrsETH is permanently unredeemable.

---

### Impact Explanation

**Critical — Permanent freezing of funds.**

All wrsETH holders lose the ability to redeem their tokens for any underlying asset. The underlying altRsETH collateral held in the contract is also permanently locked (no sweep/rescue function exists). The entire wrsETH supply becomes worthless.

---

### Likelihood Explanation

**Low-Medium.** The TIMELOCK_ROLE is a trusted governance actor, but the scenario is operationally realistic: during a token migration (e.g., replacing a deprecated altRsETH bridge token with a new one), the TIMELOCK would call `removeAllowedToken(oldToken)` before or without ensuring all wrsETH is redeemed first. The contract provides no warning or guard against this. Notably, every pool contract in the same codebase (`RSETHPool`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) correctly implements a `TokenBalanceNotZero` guard in their `removeSupportedToken` functions: [4](#0-3) 

`RsETHTokenWrapper` is the only contract in the codebase that omits this protection.

---

### Recommendation

Add a balance guard to `removeAllowedToken` mirroring the pattern used in all pool contracts:

```solidity
function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    // Prevent removing a token while the contract holds collateral for it
    if (ERC20Upgradeable(_asset).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

    allowedTokens[_asset] = false;
    emit TokenRemoved(_asset);
}
```

Additionally, consider adding a check that `totalSupply() == 0` before allowing the last allowed token to be removed, to guard against the `mint`-without-deposit bridge path.

---

### Proof of Concept

```solidity
// State-sequence test (local fork or unit test)
function test_permanentFreeze() public {
    // 1. Pool mints wrsETH to users (bridge path, no deposit)
    vm.prank(minterRole);
    wrapper.mint(userA, 50e18);
    vm.prank(minterRole);
    wrapper.mint(userB, 50e18);

    // 2. Bridger deposits collateral to back the minted supply
    vm.prank(bridgerRole);
    altRsETH.approve(address(wrapper), 100e18);
    vm.prank(bridgerRole);
    wrapper.depositBridgerAssets(address(altRsETH), 100e18);

    // 3. TIMELOCK removes the only allowed token (e.g., token migration)
    vm.prank(timelockRole);
    wrapper.removeAllowedToken(address(altRsETH));

    // 4. All withdrawals now permanently revert
    vm.prank(userA);
    vm.expectRevert(RsETHTokenWrapper.TokenNotAllowed.selector);
    wrapper.withdraw(address(altRsETH), 50e18);

    vm.prank(userB);
    vm.expectRevert(RsETHTokenWrapper.TokenNotAllowed.selector);
    wrapper.withdraw(address(altRsETH), 50e18);

    // 5. 100e18 altRsETH locked in contract, 100e18 wrsETH permanently worthless
    assertEq(altRsETH.balanceOf(address(wrapper)), 100e18); // locked forever
    assertEq(wrapper.totalSupply(), 100e18);                // unredeemable
}
```

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

**File:** contracts/L2/RsETHTokenWrapper.sol (L190-192)
```text
    function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
        _mint(_to, _amount);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L559-562)
```text
    function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();
```
