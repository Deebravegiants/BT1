### Title
Unbacked `mint()` Tokens Drain Legitimate Depositors' altAgETH via `withdraw()` — (`contracts/agETH/AGETHTokenWrapper.sol`)

### Summary

`AGETHTokenWrapper` has two distinct paths that produce fungible wrapper tokens: `deposit()` (backed 1:1 by altAgETH held in the contract) and `mint()` (no collateral required, intended for bridge/L2 use). Because `withdraw()` burns any wrapper token and transfers altAgETH from the contract's balance without distinguishing origin, bridge-minted tokens can be redeemed against altAgETH deposited by regular users, draining their collateral.

### Finding Description

`mint()` is a privileged function gated by `MINTER_ROLE`, intended to be granted to a bridge or cross-chain relay so it can represent bridged supply on L2: [1](#0-0) 

It calls `_mint()` directly — no altAgETH is transferred into the contract: [1](#0-0) 

`_withdraw()` burns wrapper tokens from `msg.sender` and transfers altAgETH from the contract's balance to the recipient, with no check on how the burned tokens were originally created: [2](#0-1) 

The backing mechanism (`depositBridgerAssets`) is a separate, optional, role-gated call that is not atomically coupled to `mint()`: [3](#0-2) 

Because wrapper tokens from both paths are fungible ERC-20 tokens, any holder of bridge-minted tokens can call `withdraw()` and receive altAgETH that was deposited by a regular user.

### Impact Explanation

**Critical — Direct theft of user funds at rest.**

Concrete scenario:
1. User A calls `deposit(altAgETH, 100e18)` → contract holds 100e18 altAgETH, User A holds 100e18 wrapper tokens.
2. Bridge (MINTER_ROLE) calls `mint(UserB, 100e18)` → contract still holds 100e18 altAgETH, but total supply is now 200e18.
3. User B calls `withdraw(altAgETH, 100e18)` → burns 100e18 wrapper tokens, receives 100e18 altAgETH.
4. Contract now holds 0 altAgETH. User A's 100e18 wrapper tokens are worthless — their deposited collateral is gone.

### Likelihood Explanation

**High.** Granting `MINTER_ROLE` to a bridge contract is the explicitly documented and intended deployment pattern. No admin compromise is required — the bridge legitimately mints tokens, and any recipient (or the bridge itself) can immediately call `withdraw()`. The window between `mint()` and `depositBridgerAssets()` is always present and exploitable by any token holder.

### Recommendation

1. **Separate accounting**: Track "deposit-backed" supply vs. "bridge-minted" supply. Only allow `withdraw()` to redeem against deposit-backed tokens.
2. **Atomic backing**: Require `depositBridgerAssets()` to be called atomically with or before `mint()`, or enforce that `balanceOf(contract) >= totalSupply()` before any withdrawal.
3. **Restrict `withdraw()` for bridge-minted tokens**: Bridge-minted tokens should only be redeemable by burning them back through the bridge, not by withdrawing altAgETH from the lockbox.

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Deploy AGETHTokenWrapper, grant MINTER_ROLE to attacker
// 1. User A deposits 100e18 altAgETH
agethWrapper.deposit(altAgETH, 100e18); // User A

// 2. Bridge (MINTER_ROLE) mints 100e18 wrapper tokens to attacker (no altAgETH deposited)
agethWrapper.mint(attacker, 100e18); // Bridge/attacker

// 3. Attacker withdraws altAgETH using unbacked wrapper tokens
agethWrapper.withdraw(altAgETH, 100e18); // Attacker

// Assert: attacker holds 100e18 altAgETH
// Assert: contract holds 0 altAgETH
// Assert: User A's 100e18 wrapper tokens are now unbacked (theft complete)
assertEq(altAgETH.balanceOf(attacker), 100e18);
assertEq(altAgETH.balanceOf(address(agethWrapper)), 0);
```

The root cause is at: [2](#0-1) 

`_withdraw()` has no invariant check that `balanceOf(contract) >= totalSupply()` after the transfer, and no mechanism to distinguish deposit-backed tokens from bridge-minted tokens.

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

**File:** contracts/agETH/AGETHTokenWrapper.sol (L143-151)
```text
    function depositBridgerAssets(address _asset, uint256 _amount) external onlyRole(BRIDGER_ROLE) {
        if (maxAmountToDepositBridgerAsset(_asset) < _amount) {
            revert CannotDeposit();
        }

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        emit BridgerDeposited(_asset, _amount);
    }
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L165-167)
```text
    function mint(address _to, uint256 _amount) external onlyRole(MINTER_ROLE) {
        _mint(_to, _amount);
    }
```
