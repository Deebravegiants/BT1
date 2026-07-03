### Title
Blocked rsETH holders bypass transfer restrictions as approved spenders due to missing `_enforceNotBlocked` on spender in `transferFrom` path - (File: contracts/RSETH.sol)

### Summary

`RSETH.sol` implements a transfer-blocking mechanism via `transfersBlockedUntil` and `_enforceNotBlocked`. The `_transfer` override enforces the block on `from` and `to`, and `mint`/`burnFrom` enforce it on the minted/burned account. However, the `approve()` function is not overridden to check whether the spender is blocked, and the `_transfer` override does not check the spender (`msg.sender`) in the `transferFrom` execution path. A blocked user who holds (or obtains) an ERC-20 allowance from another account can call `transferFrom` and move that account's rsETH without restriction, fully bypassing the block.

### Finding Description

`RSETH` overrides `_transfer` to call `_enforceNotBlocked` on both `from` and `to`: [1](#0-0) 

`mint` and `burnFrom` also call `_enforceNotBlocked` on the relevant account: [2](#0-1) [3](#0-2) 

However, `approve()` is **not** overridden. The inherited OpenZeppelin `ERC20Upgradeable.approve` records the allowance without any block check on either the owner or the spender. [4](#0-3) 

When a blocked user (Alice) is the **spender** — either because she was approved before being blocked, or because another user approved her after the block was set (which succeeds since `approve` has no block check) — she can call:

```
transferFrom(Bob, Carol, rsETHAmount)
```

The execution path is:
1. `ERC20Upgradeable.transferFrom` → `_spendAllowance(Bob, Alice, amount)` → `_transfer(Bob, Carol, amount)`
2. `_transfer` checks `_enforceNotBlocked(Bob)` and `_enforceNotBlocked(Carol)` — **neither is blocked**
3. The spender Alice is **never checked**

The transfer succeeds despite Alice being blocked.

The blocking mechanism is also used as a precursor to `recoverFrozenFunds`, which recovers a blocked user's balance to a custody address: [5](#0-4) 

If a blocked user pre-arranges an allowance to a colluding address before the block is applied (or if the colluding address calls `approve` on behalf of the blocked user after the block), the blocked user can drain their own balance via `transferFrom` before `recoverFrozenFunds` is executed, defeating the fund-recovery invariant.

### Impact Explanation

A blocked rsETH holder can:
1. Move other users' rsETH as an approved spender, bypassing the protocol's transfer restriction.
2. Drain their own blocked balance via a pre-arranged or post-block allowance before `recoverFrozenFunds` is called, defeating the fund-recovery mechanism.

This is a direct, provable discrepancy between the intended invariant (blocked accounts cannot transact) and the implementation. Impact: **temporary freezing of funds fails / contract fails to deliver promised returns** — the block is ineffective for the spender role, and frozen-fund recovery can be pre-empted.

### Likelihood Explanation

Any blocked user who holds a pre-existing ERC-20 allowance (e.g., from a DeFi integration, a DEX router, or a prior `approve` call) can immediately exploit this. Additionally, since `approve()` itself has no block check, a third party can grant an allowance to a blocked user at any time, enabling the bypass on demand. No privileged access is required beyond holding an allowance.

### Recommendation

Override `approve` (and `increaseAllowance` / `decreaseAllowance` if applicable) to enforce `_enforceNotBlocked` on both the caller and the spender:

```solidity
function approve(address spender, uint256 amount) public override returns (bool) {
    _enforceNotBlocked(_msgSender());
    _enforceNotBlocked(spender);
    return super.approve(spender, amount);
}
```

Additionally, override `transferFrom` or extend `_transfer` to also check `msg.sender` (the spender) when called via `transferFrom`, ensuring no blocked address can participate in any token movement in any role.

### Proof of Concept

1. Manager calls `blockUserTransfers([Alice])` — Alice is blocked until `block.timestamp + 1 days`.
2. Bob calls `approve(Alice, 1000e18)` — succeeds (no block check on spender).
3. Alice calls `transferFrom(Bob, Alice2, 1000e18)`.
4. `_transfer(Bob, Alice2, amount)` is invoked — checks Bob (not blocked) and Alice2 (not blocked) — **passes**.
5. Alice successfully moves 1000 rsETH despite being blocked.

Alternatively, for fund-recovery bypass:
1. Alice calls `approve(Colluder, balanceOf(Alice))` before or after being blocked.
2. Colluder calls `transferFrom(Alice, Colluder, balanceOf(Alice))` — `_transfer(Alice, ...)` checks Alice as `from` → **reverts** (Alice is blocked as sender).

> Note: The spender-bypass (step 1–5 above) is the primary attack vector. The fund-recovery bypass requires Alice to drain her own balance via a colluder *before* the block is applied, which is a separate but related concern. [6](#0-5) [1](#0-0) [7](#0-6)

### Citations

**File:** contracts/RSETH.sol (L13-13)
```text
contract RSETH is Initializable, LRTConfigRoleChecker, ERC20Upgradeable, PausableUpgradeable {
```

**File:** contracts/RSETH.sol (L161-177)
```text
    function blockUserTransfers(address[] calldata accounts) external onlyLRTManager {
        uint256 blockedUntil = block.timestamp + 1 days;
        uint256 length = accounts.length;

        for (uint256 i = 0; i < length; ++i) {
            address account = accounts[i];

            if (isPermanentlyExempt[account] || account == address(0)) continue;

            uint256 prevBlockedUntil = transfersBlockedUntil[account];

            if (blockedUntil != prevBlockedUntil) {
                transfersBlockedUntil[account] = blockedUntil;
                emit UserTransfersBlocked(account, blockedUntil);
            }
        }
    }
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

**File:** contracts/RSETH.sol (L238-239)
```text
        _enforceNotBlocked(to);
        _mint(to, amount);
```

**File:** contracts/RSETH.sol (L245-247)
```text
    function burnFrom(address account, uint256 amount) external onlyRole(LRTConstants.BURNER_ROLE) whenNotPaused {
        _enforceNotBlocked(account);
        _burn(account, amount);
```

**File:** contracts/RSETH.sol (L287-291)
```text
    function _transfer(address from, address to, uint256 amount) internal override {
        _enforceNotBlocked(from);
        _enforceNotBlocked(to);
        super._transfer(from, to, amount);
    }
```

**File:** contracts/RSETH.sol (L294-306)
```text
    function _enforceNotBlocked(address account) internal {
        // Addresses that are permanently exempt can never be blocked
        if (isPermanentlyExempt[account]) return;

        // Check if the account has an active transfer block
        uint256 blockedUntil = transfersBlockedUntil[account];
        if (blockedUntil == 0) return;

        if (block.timestamp < blockedUntil) revert TransfersBlocked(account, blockedUntil);

        // Auto-clean up expired block
        delete transfersBlockedUntil[account];
    }
```
