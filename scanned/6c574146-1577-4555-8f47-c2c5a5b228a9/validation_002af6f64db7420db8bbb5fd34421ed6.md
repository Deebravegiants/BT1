### Title
Manager Can Drain Supported Token Balances via `setKingToken` Access Control Misconfiguration — (`contracts/king-protocol/TokenSwap.sol`)

### Summary

`setKingToken` is documented as "admin only" in its NatSpec but is guarded by `onlyManager` instead of `onlyAdmin`. A single MANAGER_ROLE holder can exploit this to redirect the `kingToken` pointer to any supported ERC20 held by the contract, then call `withdrawKing` to drain that token balance to an arbitrary address.

### Finding Description

`setKingToken` at line 422 carries the NatSpec comment `/// @notice Update the KING token address (admin only)` but applies the `onlyManager` modifier: [1](#0-0) 

`withdrawKing` at line 282 is callable by any `MANAGER_ROLE` holder via `onlyAdminOrManager`. It reads `kingToken.balanceOf(address(this))` and transfers `kingToken` to an arbitrary recipient: [2](#0-1) 

Because `kingToken` is a mutable storage variable and `withdrawKing` uses it directly for both the balance check and the transfer, substituting `kingToken` with any supported ERC20 address causes `withdrawKing` to drain that token instead of KING.

### Impact Explanation

A MANAGER_ROLE holder executes the following two-step sequence with no further preconditions:

1. `setKingToken(address(stETH))` — redirects `kingToken` to stETH (or any other supported token held by the contract).
2. `withdrawKing(attacker, stETHBalance)` — `kingToken.balanceOf(address(this))` now returns the stETH balance; `kingToken.safeTransfer` sends it to the attacker.

All supported token balances at-rest in the contract are drainable. This is **direct theft of user funds at-rest**, matching the Critical scope.

### Likelihood Explanation

The MANAGER_ROLE is a single privileged role — no multi-sig or timelock is enforced at the contract level. The NatSpec explicitly states the function should be admin-only, confirming the developer's intent was for `setKingToken` to be more restricted than manager-level. The misconfiguration is a single-actor exploit requiring no collusion, no oracle manipulation, and no external dependency.

### Recommendation

Change the modifier on `setKingToken` (and `setKingProtocol`, which has the same NatSpec/modifier mismatch) from `onlyManager` to `onlyAdmin`:

```solidity
// Before (line 422)
function setKingToken(address _kingToken) external onlyManager {

// After
function setKingToken(address _kingToken) external onlyAdmin {
``` [3](#0-2) 

Additionally, consider adding a check in `withdrawKing` that the recipient is not a zero address and that `kingToken` is not a supported token address, as a defense-in-depth measure.

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Pseudocode unit test (Foundry-style)
function test_managerDrainsSupportedToken() public {
    // Setup: contract holds 1000e18 stETH (a supported token)
    deal(address(stETH), address(tokenSwap), 1000e18);

    // Step 1: manager redirects kingToken to stETH
    vm.prank(manager);
    tokenSwap.setKingToken(address(stETH));

    // Step 2: manager withdraws "KING" tokens — actually stETH
    vm.prank(manager);
    tokenSwap.withdrawKing(attacker, 1000e18);

    // Assert: stETH drained from contract to attacker
    assertEq(stETH.balanceOf(attacker), 1000e18);
    assertEq(stETH.balanceOf(address(tokenSwap)), 0);
}
```

The root cause is confirmed at:
- `setKingToken` modifier: [4](#0-3) 
- `withdrawKing` using `kingToken` directly: [5](#0-4)

### Citations

**File:** contracts/king-protocol/TokenSwap.sol (L282-297)
```text
    function withdrawKing(address recipient, uint256 amount) external nonReentrant whenNotPaused onlyAdminOrManager {
        if (amount == 0) {
            revert ZeroAmount();
        }

        UtilLib.checkNonZeroAddress(recipient);

        uint256 contractBalance = kingToken.balanceOf(address(this));
        if (contractBalance < amount) {
            revert InsufficientBalance();
        }

        kingToken.safeTransfer(recipient, amount);

        emit KingWithdrawn(recipient, amount, msg.sender);
    }
```

**File:** contracts/king-protocol/TokenSwap.sol (L411-418)
```text
    function setKingProtocol(address _kingProtocol) external onlyManager {
        UtilLib.checkNonZeroAddress(_kingProtocol);

        address oldProtocol = address(kingProtocol);
        kingProtocol = IKingProtocol(_kingProtocol);

        emit KingProtocolUpdated(oldProtocol, _kingProtocol);
    }
```

**File:** contracts/king-protocol/TokenSwap.sol (L420-429)
```text
    /// @notice Update the KING token address (admin only)
    /// @param _kingToken The new KING token address
    function setKingToken(address _kingToken) external onlyManager {
        UtilLib.checkNonZeroAddress(_kingToken);

        address oldToken = address(kingToken);
        kingToken = IERC20(_kingToken);

        emit TokenAddressUpdated("KING", oldToken, _kingToken);
    }
```
