### Title
CCIP Pool Cannot Burn User Tokens Without Prior Allowance, Blocking L2-to-L1 Bridge Flow — (`contracts/ccip/WrappedRSETH.sol`)

---

### Summary

`burn(address account, uint256 amount)` delegates unconditionally to `burnFrom`, which in turn calls OZ's `ERC20Burnable.burnFrom`. OZ's implementation requires the caller to have an ERC-20 allowance from `account`. Because the CCIP token pool (a registered burner) never receives such an allowance from users, every L2-to-L1 burn attempt reverts, permanently blocking the bridge flow until users manually pre-approve the pool.

---

### Finding Description

The call chain is:

```
burn(address account, uint256 amount)   // line 122 — no onlyBurner modifier
  └─► burnFrom(account, amount)          // line 129 — onlyBurner ✓ (pool passes)
        └─► super.burnFrom(account, amount)  // OZ ERC20Burnable
              └─► _spendAllowance(account, msg.sender, amount)  // REVERTS — no allowance
                    └─► _burn(account, amount)
``` [1](#0-0) 

`burn(address, uint256)` has **no** `onlyBurner` modifier and simply forwards to `burnFrom`: [2](#0-1) 

`burnFrom` has `onlyBurner` and calls `super.burnFrom`, which is OZ's implementation: [3](#0-2) 

OZ's `burnFrom` calls `_spendAllowance(account, _msgSender(), amount)` before `_burn`. This requires `account` (the user) to have approved `_msgSender()` (the CCIP pool) for at least `amount`. In the CCIP lock-or-burn flow, no such approval exists — the pool is supposed to burn tokens by virtue of its burner role, not via ERC-20 allowance.

The intended design (matching the Chainlink reference implementation) is that `burn(address, uint256)` should call `_burn(account, amount)` directly, bypassing the allowance check, since the `onlyBurner` role already authorises the caller.

---

### Impact Explanation

Every L2-to-L1 CCIP bridge transfer requires the token pool to call `burn(user, amount)`. Because this always reverts without a prior `approve(pool, amount)` from the user, **all L2-to-L1 bridge transfers are blocked**. Funds are not permanently lost (they remain on L2), but they are temporarily frozen until the user performs an out-of-band approval — an action that is not part of the standard CCIP UX and that most users will never know to do.

Impact: **Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

This triggers on every single L2-to-L1 bridge attempt by any user who has not manually pre-approved the CCIP pool. That is effectively every user under normal operation. No special attacker is needed; the bug is structural and deterministic.

---

### Recommendation

Replace the `burn(address, uint256)` → `burnFrom` delegation with a direct `_burn` call, guarded by `onlyBurner`:

```solidity
// CORRECT
function burn(address account, uint256 amount)
    public
    virtual
    override
    onlyBurner
{
    _burn(account, amount);
}
```

This matches the Chainlink reference `BurnMintERC677` implementation and removes the spurious allowance requirement.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "../contracts/ccip/WrappedRSETH.sol";

contract BurnFlowTest is Test {
    WrappedRSETH token;
    address owner   = address(0xA);
    address pool    = address(0xB);   // simulated CCIP token pool (burner)
    address user    = address(0xC);

    function setUp() public {
        vm.prank(owner);
        token = new WrappedRSETH("Wrapped rsETH", "wrsETH", 18, 0, owner);

        // Grant pool the burner role
        vm.prank(owner);
        token.grantBurnRole(pool);

        // Mint tokens to user (simulates L2 mint on inbound bridge)
        vm.prank(owner);
        token.grantMintRole(owner);
        vm.prank(owner);
        token.mint(user, 1 ether);
    }

    function test_ccipBurnRevertsWithoutAllowance() public {
        // CCIP pool calls burn(user, amount) — standard lock-or-burn flow
        vm.prank(pool);
        vm.expectRevert(); // ERC20: insufficient allowance
        token.burn(user, 1 ether);
    }

    function test_ccipBurnSucceedsOnlyWithPriorApproval() public {
        // User must manually approve the pool — not part of normal CCIP UX
        vm.prank(user);
        token.approve(pool, 1 ether);

        vm.prank(pool);
        token.burn(user, 1 ether); // now succeeds
        assertEq(token.balanceOf(user), 0);
    }
}
```

Running `test_ccipBurnRevertsWithoutAllowance` passes (the revert is confirmed), proving the bridge flow is broken on unmodified code without any user pre-approval.

### Citations

**File:** contracts/ccip/WrappedRSETH.sol (L122-124)
```text
    function burn(address account, uint256 amount) public virtual override {
        burnFrom(account, amount);
    }
```

**File:** contracts/ccip/WrappedRSETH.sol (L129-131)
```text
    function burnFrom(address account, uint256 amount) public override(IBurnMintERC20, ERC20Burnable) onlyBurner {
        super.burnFrom(account, amount);
    }
```

**File:** lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Burnable.sol (L35-38)
```text
    function burnFrom(address account, uint256 amount) public virtual {
        _spendAllowance(account, _msgSender(), amount);
        _burn(account, amount);
    }
```
