### Title
LRT Manager can permanently freeze and seize user rsETH with no escape mechanism — (File: contracts/RSETH.sol)

---

### Summary

`RSETH.sol` grants the LRT Manager the ability to block any user's rsETH transfers for 24 hours via `blockUserTransfers`. Because the block is unconditionally renewable and is also enforced inside `burnFrom`, a blocked user cannot transfer, sell, or initiate a withdrawal of their rsETH. The LRT Admin can then call `recoverFrozenFunds` to seize the user's entire rsETH balance to a custody address. There is no escape path for the user.

---

### Finding Description

**Step 1 — Indefinitely renewable transfer block.**

`blockUserTransfers` sets `transfersBlockedUntil[account] = block.timestamp + 1 days` for every address in the supplied list. [1](#0-0) 

The NatSpec comment explicitly documents that re-applying the block before expiry refreshes it: *"Re-applying the block before expiry refreshes the hold to `block.timestamp + 1 days` (i.e. not cumulative; never more than 24h from the latest call)."* The Manager can call this function once every 24 hours to keep the block perpetually active with no on-chain limit on repetitions. [2](#0-1) 

**Step 2 — Block enforced on all transfer paths.**

The `_transfer` override calls `_enforceNotBlocked` on both `from` and `to`, so a blocked user cannot send or receive rsETH through any ERC-20 path. [3](#0-2) 

**Step 3 — Block enforced inside `burnFrom`, closing the withdrawal exit.**

`burnFrom` — the function called by the withdrawal manager to destroy rsETH during the withdrawal lifecycle — also calls `_enforceNotBlocked(account)` before burning. [4](#0-3) 

**Step 4 — `initiateWithdrawal` requires a transfer from the user, which reverts.**

The only user-facing withdrawal entry point calls `safeTransferFrom(msg.sender, address(this), rsETHUnstaked)`. Because `safeTransferFrom` routes through the overridden `_transfer`, a blocked user's call reverts at the ERC-20 layer before any withdrawal request is recorded. [5](#0-4) 

**Step 5 — Admin can seize the frozen balance.**

While the block is active, `recoverFrozenFunds` allows the LRT Admin to transfer the user's entire rsETH balance to the `custodyAddress` by bypassing the block via a direct `super._transfer` call. [6](#0-5) 

---

### Impact Explanation

**Critical — Permanent freezing of funds and direct theft of user funds.**

A user who has deposited ETH or LSTs and holds rsETH can be rendered completely unable to transfer, sell, or redeem their position. The Manager can maintain this state indefinitely at negligible cost (one transaction per day). The Admin can then drain the frozen balance to a custody address, constituting direct theft of user funds. There is no on-chain mechanism that allows the user to bypass the block and recover their assets independently.

---

### Likelihood Explanation

The LRT Manager is a centralized role controlled by the Kelp DAO team, directly analogous to the Linea sequencer operator. Like the Linea team, the Manager can be compelled by a government entity (e.g., OFAC sanctions enforcement) to censor specific addresses. The `blockUserTransfers` + `recoverFrozenFunds` combination is an intentional design feature for regulatory compliance, meaning the code path is fully operational and requires no exploit — only a policy decision by the centralized operator. Any user whose address appears on a sanctions list is at risk.

---

### Recommendation

1. **Remove or strictly time-cap the block renewal.** Prohibit re-applying a block to an address that is already blocked, or enforce a hard maximum total block duration (e.g., 72 hours) after which the block expires unconditionally.
2. **Decouple `burnFrom` from the transfer block.** Withdrawal completion burns rsETH held by the `LRTWithdrawalManager`, not by the user. The block on the user's address should not prevent the protocol from processing a withdrawal that was already initiated and whose rsETH has already been escrowed.
3. **Provide a user escape path.** Allow a blocked user to call a permissionless function that transfers their rsETH directly into the withdrawal queue (bypassing the ERC-20 transfer block), so they retain the ability to exit their position regardless of the Manager's actions — analogous to the L1-forced-inclusion mechanism recommended in the Linea report.
4. **Separate freeze from seizure.** `recoverFrozenFunds` should require an additional time-lock or multi-sig approval before assets can be moved to the custody address, preventing unilateral seizure.

---

### Proof of Concept

```
1. Alice deposits 10 ETH into LRTDepositPool and receives rsETH.

2. LRT Manager calls:
       RSETH.blockUserTransfers([Alice])
   → transfersBlockedUntil[Alice] = block.timestamp + 1 days

3. Alice calls LRTWithdrawalManager.initiateWithdrawal(ETH_TOKEN, rsETHAmount, ""):
       IERC20(rsETH).safeTransferFrom(Alice, withdrawalManager, rsETHAmount)
       → RSETH._transfer(Alice, withdrawalManager, rsETHAmount)
       → _enforceNotBlocked(Alice)
       → revert TransfersBlocked(Alice, blockedUntil)   ← Alice is stuck

4. Every ~24 hours, Manager calls blockUserTransfers([Alice]) again.
   Alice has no on-chain action that can unblock herself.

5. LRT Admin calls:
       RSETH.recoverFrozenFunds(Alice)
       → super._transfer(Alice, custodyAddress, Alice.balance)
   Alice's entire rsETH balance is seized. Her deposited ETH is permanently lost.
```

### Citations

**File:** contracts/RSETH.sol (L156-177)
```text
    /// @notice Block transfers TO and FROM given users for 24 hours
    /// @dev Re-applying the block before expiry refreshes the hold to `block.timestamp + 1 days`
    ///      (i.e. not cumulative; never more than 24h from the latest call). Exempt addresses cannot be blocked.
    ///      Emits {UserTransfersBlocked} only when the timestamp changes.
    /// @param accounts Addresses to block.
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

**File:** contracts/RSETH.sol (L206-220)
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
    }
```

**File:** contracts/RSETH.sol (L245-248)
```text
    function burnFrom(address account, uint256 amount) external onlyRole(LRTConstants.BURNER_ROLE) whenNotPaused {
        _enforceNotBlocked(account);
        _burn(account, amount);
    }
```

**File:** contracts/RSETH.sol (L287-306)
```text
    function _transfer(address from, address to, uint256 amount) internal override {
        _enforceNotBlocked(from);
        _enforceNotBlocked(to);
        super._transfer(from, to, amount);
    }

    /// @dev Reverts if `account` is currently blocked (used for transfers, mints, and burns)
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

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```
