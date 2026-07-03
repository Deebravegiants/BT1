### Title
Admin Can Permanently Lock User Funds via `removeAllowedToken` With No Recovery Path — (`contracts/agETH/AGETHTokenWrapper.sol`)

---

### Summary

`AGETHTokenWrapper.removeAllowedToken` can be called by `DEFAULT_ADMIN_ROLE` at any time with no timelock and no corresponding `addAllowedToken` function. Once a token is removed, every user holding wrapper agETH backed by that token is permanently unable to redeem it, because `_withdraw` hard-reverts on the `allowedTokens` check.

---

### Finding Description

`_withdraw` gates redemption on `allowedTokens[_asset]`: [1](#0-0) 

`removeAllowedToken` flips that flag to `false` with no delay: [2](#0-1) 

Critically, the contract explicitly omits any `addAllowedToken` function — the comment at line 153 confirms this is intentional: [3](#0-2) 

This is a meaningful design difference from the analogous `RsETHTokenWrapper`, which gates the equivalent function behind `TIMELOCK_ROLE` (providing a delay window for users to exit): [4](#0-3) 

`AGETHTokenWrapper` has no such protection. The moment `removeAllowedToken` executes, all outstanding wrapper agETH backed by that token becomes permanently non-redeemable.

The "same-block race condition" framing in the question is technically accurate but understates the issue: the admin does not need to front-run anyone. Any call to `removeAllowedToken` — whether before, during, or after user deposits — permanently breaks the withdrawal invariant for all existing holders.

---

### Impact Explanation

Users who legitimately deposited `altAgETH` and received wrapper agETH can no longer call `withdraw` or `withdrawTo`. Their wrapper tokens still exist and the underlying `altAgETH` remains in the contract, so no value is destroyed — but the redemption path is permanently severed with no on-chain recovery mechanism. This matches **Low: Contract fails to deliver promised returns, but doesn't lose value**.

---

### Likelihood Explanation

The trigger is a single admin transaction with no timelock, no multi-sig requirement enforced at the contract level, and no `addAllowedToken` escape hatch. The admin may act in good faith (e.g., deprecating a bridged variant), unaware that doing so permanently bricks existing holders. The absence of a timelock (present in the sister contract) makes accidental or rushed execution realistic.

---

### Recommendation

1. Add a timelock delay before `removeAllowedToken` takes effect, matching the pattern in `RsETHTokenWrapper` (`TIMELOCK_ROLE`), so users have a window to exit.
2. Add an `addAllowedToken` function (admin/timelock-gated) so the state can be reversed if needed.
3. Alternatively, allow `withdraw` to succeed even for de-listed tokens when the caller holds a positive wrapper balance backed by that token (i.e., separate "can deposit" from "can withdraw").

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.27;

import "forge-std/Test.sol";
import "contracts/agETH/AGETHTokenWrapper.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockAltAgETH is ERC20 {
    constructor() ERC20("altAgETH", "altAgETH") {
        _mint(msg.sender, 1000 ether);
    }
}

contract RaceConditionTest is Test {
    AGETHTokenWrapper wrapper;
    MockAltAgETH altToken;
    address admin = address(0xA);
    address user  = address(0xB);

    function setUp() public {
        altToken = new MockAltAgETH();
        wrapper  = new AGETHTokenWrapper();
        wrapper.initialize(admin, admin, address(altToken));

        // Fund user and approve
        altToken.transfer(user, 100 ether);
        vm.prank(user);
        altToken.approve(address(wrapper), 100 ether);

        // User deposits
        vm.prank(user);
        wrapper.deposit(address(altToken), 100 ether);
    }

    function testAdminRemoveThenWithdrawReverts() public {
        // Admin removes token (same block or any block)
        vm.prank(admin);
        wrapper.removeAllowedToken(address(altToken));

        // User's withdraw now reverts permanently — no addAllowedToken exists
        vm.prank(user);
        vm.expectRevert(AGETHTokenWrapper.TokenNotAllowed.selector);
        wrapper.withdraw(address(altToken), 100 ether);

        // User still holds wrapper agETH — value trapped
        assertEq(wrapper.balanceOf(user), 100 ether);
    }
}
```

Running `forge test` on unmodified code will show the `withdraw` revert and the user's wrapper balance unchanged, confirming the invariant break.

### Citations

**File:** contracts/agETH/AGETHTokenWrapper.sol (L111-112)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();
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

**File:** contracts/L2/RsETHTokenWrapper.sol (L180-185)
```text
    function removeAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        allowedTokens[_asset] = false;
        emit TokenRemoved(_asset);
    }
```
