### Title
`WrappedRSETH.burn(uint256)` Restricts Self-Burn to Privileged Burners, Breaking `ERC20Burnable` and `IBurnMintERC20` Promises - ([File: contracts/ccip/WrappedRSETH.sol])

---

### Summary

`WrappedRSETH` inherits from both `ERC20Burnable` and `IBurnMintERC20`, both of which promise that any token holder can burn their own balance via `burn(uint256)`. However, the override applies the `onlyBurner` modifier, silently restricting this to a privileged set. An ordinary holder with a positive balance cannot burn their own tokens.

---

### Finding Description

`WrappedRSETH` declares:

```solidity
contract WrappedRSETH is IBurnMintERC20, ERC677, IERC165, ERC20Burnable, ConfirmedOwnerWithProposal
``` [1](#0-0) 

The `burn(uint256)` override is:

```solidity
function burn(uint256 amount) public override(IBurnMintERC20, ERC20Burnable) onlyBurner {
    super.burn(amount);
}
``` [2](#0-1) 

The `onlyBurner` modifier enforces:

```solidity
modifier onlyBurner() {
    if (!isBurner(msg.sender)) revert SenderNotBurner(msg.sender);
    _;
}
``` [3](#0-2) 

`isBurner` checks membership in `s_burners`, a set managed exclusively by the owner. [4](#0-3) 

OpenZeppelin's `ERC20Burnable.burn(uint256)` carries no access control — it is explicitly designed so any holder can destroy their own tokens. By overriding it with `onlyBurner`, `WrappedRSETH` silently breaks that contract.

`IBurnMintERC20` also declares `burn(uint256 amount)` with the NatSpec "Burns tokens from the sender", implying the caller is the one burning their own balance with no role prerequisite. [5](#0-4) 

---

### Impact Explanation

Any wrsETH holder who is not in `s_burners` cannot burn their own tokens. Their balance is permanently locked from self-destruction. No funds are lost (tokens remain in the holder's wallet), but the functionality promised by both `ERC20Burnable` and `IBurnMintERC20` is not delivered.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

This is deterministic and always reachable. Any address that receives wrsETH tokens (e.g., via a minter) but is not explicitly granted the burner role will hit this revert on every `burn(uint256)` call. No special conditions, timing, or attacker sophistication required.

---

### Recommendation

Two options:

1. **Remove `onlyBurner` from `burn(uint256)`** so any holder can burn their own balance (matching `ERC20Burnable` semantics), while keeping `onlyBurner` on `burnFrom` and `burn(address, uint256)` which burn *other* accounts' tokens.

2. **Remove the `ERC20Burnable` inheritance** and update the NatSpec on `IBurnMintERC20.burn(uint256)` to explicitly document that only permissioned burners may call it, so the interface contract accurately reflects the implementation.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "../contracts/ccip/WrappedRSETH.sol";

contract BurnAccessTest is Test {
    WrappedRSETH token;
    address owner  = address(0x1);
    address minter = address(0x2);
    address alice  = address(0x3);

    function setUp() public {
        vm.prank(owner);
        token = new WrappedRSETH("Wrapped rsETH", "wrsETH", 18, 0, owner);

        vm.prank(owner);
        token.grantMintRole(minter);

        // Mint tokens to alice — she is NOT a burner
        vm.prank(minter);
        token.mint(alice, 1 ether);
    }

    function testAliceCannotBurnOwnTokens() public {
        assertEq(token.balanceOf(alice), 1 ether);

        // alice tries to burn her own tokens
        vm.prank(alice);
        vm.expectRevert(
            abi.encodeWithSelector(WrappedRSETH.SenderNotBurner.selector, alice)
        );
        token.burn(1 ether);

        // balance unchanged — promised burn functionality not delivered
        assertEq(token.balanceOf(alice), 1 ether);
    }
}
```

The test deploys `WrappedRSETH` with no burners, mints to `alice`, and confirms her `burn(1 ether)` call reverts with `SenderNotBurner` while her balance remains unchanged — directly proving the broken invariant.

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

**File:** contracts/ccip/WrappedRSETH.sol (L209-211)
```text
    function isBurner(address burner) public view returns (bool) {
        return s_burners.contains(burner);
    }
```

**File:** contracts/ccip/WrappedRSETH.sol (L222-225)
```text
    modifier onlyBurner() {
        if (!isBurner(msg.sender)) revert SenderNotBurner(msg.sender);
        _;
    }
```

**File:** contracts/ccip/IBurnMintERC20.sol (L13-16)
```text
    /// @notice Burns tokens from the sender.
    /// @param amount The number of tokens to be burned.
    /// @dev this function decreases the total supply.
    function burn(uint256 amount) external;
```
