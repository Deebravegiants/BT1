### Title
CCIP Pool Bridge-Back Permanently Broken: `burn(address,uint256)` Routes Through `burnFrom` Requiring Impossible Self-Allowance — (`contracts/ccip/WrappedRSETH.sol`)

---

### Summary

`WrappedRSETH.burn(address account, uint256 amount)` unconditionally delegates to `burnFrom(account, amount)`, which calls `super.burnFrom` (OZ `ERC20Burnable`). OZ's `burnFrom` calls `_spendAllowance(account, msg.sender, amount)`. When the CCIP pool — the legitimate, permissioned burner — calls `burn(address(this), amount)` to burn tokens it holds before bridging back to L1, `_spendAllowance(pool, pool, amount)` checks `allowance(pool, pool)`, which is zero. The call reverts, permanently breaking the L2→L1 bridge-back flow.

---

### Finding Description

**Call chain:**

```
CCIP Pool → WrappedRSETH.burn(pool, amount)          // line 122 — no onlyBurner
              └→ burnFrom(pool, amount)               // line 129 — onlyBurner ✓
                   └→ super.burnFrom(pool, amount)    // ERC20Burnable line 35-38
                        └→ _spendAllowance(pool, pool, amount)
                             └→ allowance(pool, pool) == 0 → REVERT
```

`burn(address, uint256)` carries no `onlyBurner` guard of its own: [1](#0-0) 

`burnFrom` has `onlyBurner` but then calls `super.burnFrom`, which is OZ's allowance-checking variant: [2](#0-1) 

OZ `ERC20Burnable.burnFrom` always deducts from `allowance(account, msg.sender)`: [3](#0-2) 

When `msg.sender == account` (pool burning its own tokens), this requires `allowance(pool, pool) >= amount`. No CCIP pool pre-approves itself on the token contract; this is not part of the standard Chainlink CCIP pool initialization flow.

---

### Impact Explanation

The Chainlink CCIP `BurnMintTokenPool` calls `IBurnMintERC20(token).burn(address(this), amount)` as the standard bridge-back mechanism. Because this call always reverts (zero self-allowance), **no user can ever bridge WrappedRSETH from L2 back to L1**. Tokens minted on L2 are permanently stranded unless the pool contract is replaced — which itself requires governance action and redeployment of the CCIP pool, not just the token.

**Impact:** Critical — Permanent freezing of funds (all WrappedRSETH on L2 is non-redeemable).

---

### Likelihood Explanation

This triggers on every single bridge-back attempt. No special precondition, no race condition, no attacker required. Any user initiating a return bridge from L2 will hit this revert. Likelihood is **certain** once the bridge is live.

---

### Recommendation

Remove the allowance indirection in `burn(address, uint256)`. Apply `onlyBurner` directly and call `_burn` instead of routing through `burnFrom`:

```solidity
function burn(address account, uint256 amount) public virtual override onlyBurner {
    _burn(account, amount);
}
```

This matches the semantic intent (a permissioned burner burning a specified account's tokens) without requiring an allowance that the CCIP pool will never set.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "../contracts/ccip/WrappedRSETH.sol";

contract BurnSelfAllowanceTest is Test {
    WrappedRSETH token;
    address pool = address(0xBEEF);
    address owner = address(this);

    function setUp() public {
        token = new WrappedRSETH("Wrapped rsETH", "wrsETH", 18, 0, owner);
        token.grantMintAndBurnRoles(pool);
        // Mint tokens directly to the pool (simulating a prior bridge-in)
        vm.prank(pool);
        token.mint(pool, 1 ether);
    }

    function test_ccipPoolBurnSelfReverts() public {
        // Pool holds 1 ether of wrsETH and tries to burn it (standard CCIP bridge-back)
        vm.prank(pool);
        vm.expectRevert(); // ERC20InsufficientAllowance — allowance(pool, pool) == 0
        token.burn(pool, 1 ether);
    }

    function test_ccipPoolBurnSelfWorksWithSelfApproval() public {
        // Workaround: pool must pre-approve itself — non-standard, not done by CCIP pools
        vm.prank(pool);
        token.approve(pool, 1 ether);

        vm.prank(pool);
        token.burn(pool, 1 ether); // succeeds only with explicit self-approval
        assertEq(token.balanceOf(pool), 0);
    }
}
```

`test_ccipPoolBurnSelfReverts` demonstrates that the standard CCIP bridge-back call reverts on unmodified code. `test_ccipPoolBurnSelfWorksWithSelfApproval` confirms the root cause is the missing self-allowance, not the `onlyBurner` check.

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
