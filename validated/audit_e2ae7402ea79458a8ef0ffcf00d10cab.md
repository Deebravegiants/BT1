Audit Report

## Title
`_transfer` Override Missing `whenNotPaused` Guard Allows Token Transfers While Paused - (File: contracts/RSETH.sol)

## Summary
`RSETH` inherits `ERC20Upgradeable` and `PausableUpgradeable` independently and does not use `ERC20PausableUpgradeable`. The overridden `_transfer` function enforces per-address blocks via `_enforceNotBlocked` but omits a `whenNotPaused` check. Any rsETH holder can call the standard `transfer` or `transferFrom` functions to move tokens freely while the contract is paused, defeating the emergency-freeze mechanism.

## Finding Description
`RSETH._transfer` is overridden at lines 287–291:

```solidity
function _transfer(address from, address to, uint256 amount) internal override {
    _enforceNotBlocked(from);
    _enforceNotBlocked(to);
    super._transfer(from, to, amount);
}
```

There is no `whenNotPaused` modifier. The base `ERC20Upgradeable._transfer` (line 227–245) calls `_beforeTokenTransfer`, which is an empty virtual hook — it carries no pause logic. `RSETH` does not override `_beforeTokenTransfer` to add one either.

By contrast, `mint` (line 235) and `burnFrom` (line 245) both carry `whenNotPaused`, creating an asymmetry: minting and burning are blocked when paused, but peer-to-peer transfers are not.

The public `transfer` and `transferFrom` entry points in `ERC20Upgradeable` (lines 118–122 and 163–168) both resolve to `RSETH._transfer`, which never consults `paused()`.

**Exploit path:**
1. Admin detects suspicious activity and calls `pause()` as `PAUSER_ROLE`.
2. Any rsETH holder calls `rsETH.transfer(recipient, balance)`.
3. `_enforceNotBlocked` passes (address not individually blocked), no pause check exists — call succeeds.
4. Tokens move. Admin subsequently calls `blockUserTransfers([holder])` then `recoverFrozenFunds(holder)` — reverts with `NoActiveTransferBlock` or recovers 0 tokens because the balance has already moved.

## Impact Explanation
The pause mechanism is the protocol's primary emergency-stop for rsETH. Its failure to cover `transfer`/`transferFrom` means a complete token freeze cannot be achieved during an incident. A user under investigation can front-run `blockUserTransfers` by transferring tokens to a fresh address immediately after the contract is paused, rendering `recoverFrozenFunds` ineffective. This concretely matches the allowed impact: **Medium — Temporary freezing of funds** (the intended freeze fails to materialize for the primary ERC-20 transfer paths).

## Likelihood Explanation
Any rsETH holder can trigger this with a single standard `transfer` call the moment the contract is paused. No special privileges, complex setup, or victim mistakes are required. The `pause()` function is callable by `PAUSER_ROLE` and is a documented operational scenario, making the precondition realistic and repeatable.

## Recommendation
Add `whenNotPaused` to the `_transfer` override:

```solidity
function _transfer(address from, address to, uint256 amount) internal override whenNotPaused {
    _enforceNotBlocked(from);
    _enforceNotBlocked(to);
    super._transfer(from, to, amount);
}
```

Alternatively, inherit from `ERC20PausableUpgradeable` instead of plain `ERC20Upgradeable`, which enforces the pause inside `_beforeTokenTransfer` and uniformly covers `_transfer`, `_mint`, and `_burn`.

## Proof of Concept
Foundry test sequence:

```solidity
function test_transferBypassesPause() public {
    // Setup: mint rsETH to alice
    vm.prank(minter);
    rsETH.mint(alice, 1000e18);

    // Admin pauses the contract
    vm.prank(pauser);
    rsETH.pause();
    assertTrue(rsETH.paused());

    // Alice transfers while paused — should revert but succeeds
    vm.prank(alice);
    rsETH.transfer(bob, 1000e18); // succeeds, no revert

    assertEq(rsETH.balanceOf(alice), 0);
    assertEq(rsETH.balanceOf(bob), 1000e18);

    // Admin tries to recover — fails because balance is gone
    vm.prank(manager);
    rsETH.blockUserTransfers(toArray(alice));
    vm.prank(admin);
    vm.expectRevert(); // NoActiveTransferBlock or recovers 0
    rsETH.recoverFrozenFunds(alice);
}
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/RSETH.sol (L13-13)
```text
contract RSETH is Initializable, LRTConfigRoleChecker, ERC20Upgradeable, PausableUpgradeable {
```

**File:** contracts/RSETH.sol (L206-219)
```text
    function recoverFrozenFunds(address from) external onlyLRTAdmin {
        UtilLib.checkNonZeroAddress(from);
        UtilLib.checkNonZeroAddress(custodyAddress);

        if (isPermanentlyExempt[from]) revert AddressPermanentlyExempt(from);

        uint256 blockedUntil = transfersBlockedUntil[from];
        if (blockedUntil == 0 || block.timestamp >= blockedUntil) revert NoActiveTransferBlock(from);

        uint256 accountBalance = balanceOf(from);

        // Bypass transfer block enforcement when transferring to custody address
        super._transfer(from, custodyAddress, accountBalance);
        emit FrozenFundsRecovered(from, custodyAddress, accountBalance);
```

**File:** contracts/RSETH.sol (L229-248)
```text
    function mint(
        address to,
        uint256 amount
    )
        external
        onlyRole(LRTConstants.MINTER_ROLE)
        whenNotPaused
        checkDailyMintLimit(amount)
    {
        _enforceNotBlocked(to);
        _mint(to, amount);
    }

    /// @notice Burns rsETH when called by an authorized caller
    /// @param account the account to burn from
    /// @param amount the amount of rsETH to burn
    function burnFrom(address account, uint256 amount) external onlyRole(LRTConstants.BURNER_ROLE) whenNotPaused {
        _enforceNotBlocked(account);
        _burn(account, amount);
    }
```

**File:** contracts/RSETH.sol (L287-291)
```text
    function _transfer(address from, address to, uint256 amount) internal override {
        _enforceNotBlocked(from);
        _enforceNotBlocked(to);
        super._transfer(from, to, amount);
    }
```

**File:** lib/openzeppelin-contracts-upgradeable/contracts/token/ERC20/ERC20Upgradeable.sol (L227-245)
```text
    function _transfer(address from, address to, uint256 amount) internal virtual {
        require(from != address(0), "ERC20: transfer from the zero address");
        require(to != address(0), "ERC20: transfer to the zero address");

        _beforeTokenTransfer(from, to, amount);

        uint256 fromBalance = _balances[from];
        require(fromBalance >= amount, "ERC20: transfer amount exceeds balance");
        unchecked {
            _balances[from] = fromBalance - amount;
            // Overflow not possible: the sum of all balances is capped by totalSupply, and the sum is preserved by
            // decrementing then incrementing.
            _balances[to] += amount;
        }

        emit Transfer(from, to, amount);

        _afterTokenTransfer(from, to, amount);
    }
```

**File:** lib/openzeppelin-contracts-upgradeable/contracts/token/ERC20/ERC20Upgradeable.sol (L353-353)
```text
    function _beforeTokenTransfer(address from, address to, uint256 amount) internal virtual {}
```
