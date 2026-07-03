### Title
Uncollateralized `mint()` inflates `totalSupply` above altAgETH balance, permanently freezing legitimate depositors' funds — (`contracts/agETH/AGETHTokenWrapper.sol`)

---

### Summary

`AGETHTokenWrapper.mint()` is designed to issue wrapped agETH on L2 for cross-chain bridge flows **without any immediate altAgETH collateral deposit**. Because `_withdraw()` transfers altAgETH 1:1 against the contract's balance with no solvency check, any holder of bridge-minted wrapped agETH can drain the altAgETH deposited by `deposit()` users, permanently preventing those users from withdrawing.

---

### Finding Description

`mint()` (line 165–167) calls `_mint(_to, _amount)` directly with no `safeTransferFrom`: [1](#0-0) 

`_deposit()` (line 125–132) does the opposite — it pulls altAgETH in and mints wrapped tokens 1:1: [2](#0-1) 

`_withdraw()` (line 111–119) burns wrapped tokens and calls `safeTransfer` for the **exact requested amount** with no check that `altAgETH.balanceOf(address(this)) >= _amount`: [3](#0-2) 

The design intent is that `depositBridgerAssets()` (line 143–151) is called later by `BRIDGER_ROLE` to back the bridge-minted tokens. However, there is **no atomicity or ordering enforcement** between `mint()` and `depositBridgerAssets()`. Both bridge-minted tokens and deposit-backed tokens are fungible wrapped agETH, and `_withdraw()` draws from the same shared altAgETH pool. [4](#0-3) 

---

### Impact Explanation

**Critical — Permanent freezing of funds / theft of deposited altAgETH.**

Concrete scenario:

1. User A calls `deposit(altAgETH, 100e18)` → contract holds 100e18 altAgETH, `totalSupply = 100e18`.
2. MINTER_ROLE calls `mint(userB, 200e18)` (legitimate bridge operation, collateral not yet deposited) → contract still holds 100e18 altAgETH, `totalSupply = 300e18`.
3. User B calls `withdraw(altAgETH, 100e18)` → burns 100e18, `safeTransfer` succeeds, contract now holds 0 altAgETH.
4. User A calls `withdraw(altAgETH, 100e18)` → burns 100e18, `safeTransfer` **reverts** (balance = 0).

User A's 100e18 altAgETH is permanently inaccessible. User B still holds 100e18 uncollateralized wrapped agETH. This is a direct theft of User A's deposited funds.

---

### Likelihood Explanation

**High.** `mint()` is the intended cross-chain bridge path — it is called every time a user bridges agETH from L1 to L2. The window between `mint()` and the corresponding `depositBridgerAssets()` call is a normal operational state, not an edge case. Any bridge recipient can call `withdraw()` during this window. No malicious MINTER_ROLE is required; the design itself creates the race condition.

---

### Recommendation

Enforce solvency at withdrawal time, or segregate bridge-minted tokens from deposit-backed tokens:

**Option A (solvency check):** In `_withdraw()`, revert if `ERC20Upgradeable(_asset).balanceOf(address(this)) < _amount` before burning.

**Option B (atomic collateralization):** Require `depositBridgerAssets()` to be called atomically with `mint()` (e.g., in a single bridge callback), so `totalSupply` never exceeds the altAgETH balance.

**Option C (separate accounting):** Track bridge-minted supply separately and restrict `withdraw()` for bridge-minted tokens until the corresponding collateral has been deposited.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Pseudocode — run on a local fork or Foundry test

function testPermanentFreeze() public {
    // Setup
    altAgETH.mint(userA, 100e18);
    vm.prank(userA);
    altAgETH.approve(address(wrapper), 100e18);

    // Step 1: User A deposits 100e18 altAgETH
    vm.prank(userA);
    wrapper.deposit(address(altAgETH), 100e18);
    // wrapper.balanceOf(userA) == 100e18
    // altAgETH.balanceOf(wrapper) == 100e18

    // Step 2: MINTER_ROLE mints 200e18 to userB (bridge operation, no collateral yet)
    vm.prank(minterRole);
    wrapper.mint(userB, 200e18);
    // wrapper.totalSupply() == 300e18
    // altAgETH.balanceOf(wrapper) == 100e18  ← undercollateralized

    // Step 3: User B withdraws 100e18 (drains the pool)
    vm.prank(userB);
    wrapper.withdraw(address(altAgETH), 100e18);
    // altAgETH.balanceOf(wrapper) == 0

    // Step 4: User A tries to withdraw — REVERTS
    vm.prank(userA);
    vm.expectRevert();  // safeTransfer fails: insufficient balance
    wrapper.withdraw(address(altAgETH), 100e18);
    // User A's 100e18 altAgETH is permanently frozen
}
``` [5](#0-4)

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

**File:** contracts/agETH/AGETHTokenWrapper.sol (L125-131)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, _to, _amount);
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
