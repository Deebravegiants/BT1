### Title
Permanent Exemptions Cannot Be Revoked, Preventing Emergency Freeze of Compromised Exempt Addresses — (File: contracts/RSETH.sol)

---

### Summary

`RSETH.sol` contains an `addPermanentExemptions()` function that irreversibly marks addresses as permanently exempt from all transfer blocks. There is no corresponding removal function. Once an address is permanently exempt, it bypasses every enforcement path (`_enforceNotBlocked`, `blockUserTransfers`, `recoverFrozenFunds`), and this state can never be undone by any role in the contract.

---

### Finding Description

`addPermanentExemptions()` sets `isPermanentlyExempt[account] = true` and the NatSpec comment explicitly acknowledges the design as "non-reversible": [1](#0-0) 

No function exists anywhere in the contract to set `isPermanentlyExempt[account]` back to `false`. A search across all contracts confirms `isPermanentlyExempt` is only written in `addPermanentExemptions`.

Three separate enforcement paths are permanently disabled for exempt addresses:

1. **`blockUserTransfers`** silently skips exempt addresses with `continue`: [2](#0-1) 

2. **`_enforceNotBlocked`** returns immediately for exempt addresses, bypassing the block check on every `_transfer`, `mint`, and `burnFrom`: [3](#0-2) 

3. **`recoverFrozenFunds`** explicitly reverts with `AddressPermanentlyExempt` when called on an exempt address: [4](#0-3) 

Permanent exemptions are expected to be granted to protocol-critical contracts — bridges, L2 pool contracts, wrappers — so that normal protocol operations are never accidentally blocked. These are exactly the contracts that hold or route large rsETH balances on behalf of users.

---

### Impact Explanation

If any permanently exempt address is later found to be compromised (e.g., a bridge contract is exploited, a wrapper is upgraded maliciously, or a pool is drained), the admin has **zero recourse**:

- `blockUserTransfers` cannot freeze the address.
- `recoverFrozenFunds` cannot seize its rsETH balance.
- The compromised address can freely transfer rsETH to any destination without restriction.

All rsETH held by or routable through the compromised exempt address is permanently unrecoverable via the freeze mechanism. This constitutes **permanent freezing of the recovery capability** and, in an active exploit scenario, **direct theft of user funds** held in or routed through that address.

**Impact: Critical — Permanent freezing of funds / Direct theft of user funds.**

---

### Likelihood Explanation

Permanent exemptions are a deliberate operational choice granted to high-value protocol contracts (bridges, wrappers, pools). These contracts are complex, upgradeable, and interact with external systems — they represent a realistic attack surface. The inability to revoke exemptions means a single compromised exempt contract permanently disables the protocol's emergency freeze mechanism for that address. Likelihood is **Low** in isolation but the consequence is unbounded, and the design flaw is present from the moment any address is exempted.

---

### Recommendation

Add a `removePermanentExemption` function (or modify `addPermanentExemptions` to accept a `bool` flag, analogous to `setUserWhitelisted` in `LRTConverter.sol`):

```solidity
function removePermanentExemption(address account) external onlyLRTManager {
    if (!isPermanentlyExempt[account]) revert NotPermanentlyExempt(account);
    isPermanentlyExempt[account] = false;
    emit PermanentExemptionRemoved(account);
}
```

This mirrors the fix recommended in the reference report: pass a boolean to enable/disable the state, or provide a paired reversal function, so the owner can respond to security incidents without being permanently locked out.

---

### Proof of Concept

1. Manager calls `addPermanentExemptions([bridgeContract])` — `isPermanentlyExempt[bridgeContract] = true`. [5](#0-4) 

2. `bridgeContract` is later exploited; attacker controls it.

3. Admin attempts `blockUserTransfers([bridgeContract])` — silently skipped at line 168, no state change. [2](#0-1) 

4. Admin attempts `recoverFrozenFunds(bridgeContract)` — reverts with `AddressPermanentlyExempt`. [4](#0-3) 

5. Attacker freely calls `transfer` from `bridgeContract` to drain all rsETH; `_enforceNotBlocked` returns without reverting. [3](#0-2) 

6. No function exists to revoke the exemption. The state is permanent and irreversible. [6](#0-5)

### Citations

**File:** contracts/RSETH.sol (L130-154)
```text
    /// @notice Permanently add accounts to the exempted list (non-reversible)
    /// @param accounts Accounts to mark as permanently exempt (cannot have transfers blocked)
    function addPermanentExemptions(address[] calldata accounts) external onlyLRTManager {
        uint256 length = accounts.length;

        for (uint256 i = 0; i < length; ++i) {
            address account = accounts[i];
            UtilLib.checkNonZeroAddress(account);

            // Ensure the account is not currently blocked
            uint256 blockedUntil = transfersBlockedUntil[account];
            if (blockedUntil != 0) {
                if (block.timestamp < blockedUntil) {
                    revert CannotPermanentlyExemptBlockedAddress(account, blockedUntil);
                }
                // Auto-clean up expired block
                delete transfersBlockedUntil[account];
            }

            if (!isPermanentlyExempt[account]) {
                isPermanentlyExempt[account] = true;
                emit PermanentExemptionAdded(account);
            }
        }
    }
```

**File:** contracts/RSETH.sol (L168-168)
```text
            if (isPermanentlyExempt[account] || account == address(0)) continue;
```

**File:** contracts/RSETH.sol (L210-210)
```text
        if (isPermanentlyExempt[from]) revert AddressPermanentlyExempt(from);
```

**File:** contracts/RSETH.sol (L294-296)
```text
    function _enforceNotBlocked(address account) internal {
        // Addresses that are permanently exempt can never be blocked
        if (isPermanentlyExempt[account]) return;
```
