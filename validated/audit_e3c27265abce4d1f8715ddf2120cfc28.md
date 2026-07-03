### Title
`WrappedRSETH.burn(uint256)` Overrides `ERC20Burnable` with `onlyBurner`, Blocking Self-Burn for Token Holders - ([File: contracts/ccip/WrappedRSETH.sol])

---

### Summary

`WrappedRSETH` inherits `ERC20Burnable` and implements `IBurnMintERC20`, both of which carry the expectation that any token holder can burn their own balance via `burn(uint256)`. The override at line 115 applies the `onlyBurner` modifier, making the function revert for any caller not in `s_burners`. This is a concrete, testable deviation from the inherited interface's promise.

---

### Finding Description

`WrappedRSETH` declares inheritance from `ERC20Burnable`: [1](#0-0) 

OpenZeppelin's `ERC20Burnable.burn(uint256)` is explicitly unrestricted — any holder may call it to destroy their own tokens. `WrappedRSETH` overrides this function and adds `onlyBurner`: [2](#0-1) 

The `onlyBurner` modifier reverts unconditionally for any address not in `s_burners`: [3](#0-2) 

`IBurnMintERC20` also declares `burn(uint256)` with the NatSpec "Burns tokens from the sender", implying self-service burning: [4](#0-3) 

Because `s_burners` is populated only by the owner via `grantBurnRole`, an ordinary token holder who received wrsETH (e.g., via a minter) has no path to burn their own balance.

---

### Impact Explanation

No funds are lost — the holder's balance is unchanged after the revert. The impact is purely functional: the contract advertises `ERC20Burnable` semantics but silently removes the self-burn capability for all non-privileged holders. Any integrator or user relying on the standard `ERC20Burnable` interface will receive unexpected reverts.

**Scope match:** Low — Contract fails to deliver promised returns, but doesn't lose value.

---

### Likelihood Explanation

This is deterministic and unconditional. Every call to `burn(uint256)` from a non-burner address will revert, regardless of balance, approval state, or any other runtime condition. No special setup is required to trigger it.

---

### Recommendation

Two options:

1. **Remove `ERC20Burnable` from the inheritance chain** if self-burn by arbitrary holders is intentionally unsupported. This makes the access restriction explicit rather than hidden behind an inherited interface.
2. **Allow self-burn without the burner role** by splitting the modifier: permit `msg.sender` to burn their own tokens unconditionally, while requiring `onlyBurner` only for burning from another account (i.e., `burnFrom`).

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "../contracts/ccip/WrappedRSETH.sol";

contract BurnAccessTest is Test {
    WrappedRSETH token;
    address owner   = address(0xA);
    address minter  = address(0xB);
    address alice   = address(0xC);

    function setUp() public {
        vm.prank(owner);
        token = new WrappedRSETH("Wrapped rsETH", "wrsETH", 18, 0, owner);

        // Grant mint role only; no burn role granted to anyone
        vm.prank(owner);
        token.grantMintRole(minter);

        // Mint tokens to alice
        vm.prank(minter);
        token.mint(alice, 1 ether);
    }

    function test_holderCannotBurnOwnTokens() public {
        assertEq(token.balanceOf(alice), 1 ether);

        // Alice attempts to burn her own tokens — must revert
        vm.prank(alice);
        vm.expectRevert(
            abi.encodeWithSelector(WrappedRSETH.SenderNotBurner.selector, alice)
        );
        token.burn(1 ether);

        // Balance is unchanged
        assertEq(token.balanceOf(alice), 1 ether);
    }
}
```

The test deploys `WrappedRSETH` with no burners registered, mints 1 wrsETH to `alice`, and asserts that `alice`'s call to `burn(1 ether)` reverts with `SenderNotBurner` while her balance remains intact — directly proving the deviation from `ERC20Burnable`'s promise.

### Citations

**File:** contracts/ccip/WrappedRSETH.sol (L20-20)
```text
contract WrappedRSETH is IBurnMintERC20, ERC677, IERC165, ERC20Burnable, ConfirmedOwnerWithProposal {
```

**File:** contracts/ccip/WrappedRSETH.sol (L115-117)
```text
    function burn(uint256 amount) public override(IBurnMintERC20, ERC20Burnable) onlyBurner {
        super.burn(amount);
    }
```

**File:** contracts/ccip/WrappedRSETH.sol (L222-224)
```text
    modifier onlyBurner() {
        if (!isBurner(msg.sender)) revert SenderNotBurner(msg.sender);
        _;
```

**File:** contracts/ccip/IBurnMintERC20.sol (L13-16)
```text
    /// @notice Burns tokens from the sender.
    /// @param amount The number of tokens to be burned.
    /// @dev this function decreases the total supply.
    function burn(uint256 amount) external;
```
