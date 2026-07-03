### Title
Updating `rsETH` contract address in `LRTConfig` while pending withdrawals exist permanently freezes queued user funds — (File: `contracts/LRTConfig.sol`)

### Summary

`LRTConfig.setRSETH()` allows the admin to replace the `rsETH` token address at any time with no guard on in-flight withdrawal state. `LRTWithdrawalManager` pulls rsETH from users at `initiateWithdrawal` time using the then-current `lrtConfig.rsETH()`, but burns it at `unlockQueue` time using the then-current `lrtConfig.rsETH()`. If the address changes between those two calls, the burn targets a contract that holds no balance for the withdrawal manager, causing every pending `unlockQueue` call to revert and permanently freezing all queued user funds.

### Finding Description

`LRTConfig.setRSETH()` unconditionally overwrites the `rsETH` storage variable:

```solidity
// contracts/LRTConfig.sol L215-219
function setRSETH(address rsETH_) external onlyRole(DEFAULT_ADMIN_ROLE) {
    UtilLib.checkNonZeroAddress(rsETH_);
    rsETH = rsETH_;
    emit SetRSETH(rsETH_);
}
```

There is no check that the `LRTWithdrawalManager` holds zero rsETH balance before the update is allowed.

When a user calls `initiateWithdrawal`, the contract pulls rsETH from the user using the address that is current at that moment:

```solidity
// contracts/LRTWithdrawalManager.sol L166
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

The withdrawal manager now holds tokens of the **old** rsETH contract. Later, when the operator calls `unlockQueue`, the burn is issued against whatever `lrtConfig.rsETH()` returns **at that point**:

```solidity
// contracts/LRTWithdrawalManager.sol L305
if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
```

If `setRSETH` was called in between, `lrtConfig.rsETH()` now returns the **new** rsETH contract. The withdrawal manager holds zero balance of the new token, so `burnFrom` reverts with an ERC-20 insufficient-balance error. Because `_unlockWithdrawalRequests` already advanced `nextLockedNonce` in storage before the burn is attempted, the entire `unlockQueue` transaction reverts, and the queue is stuck.

### Impact Explanation

All rsETH tokens deposited by users into the withdrawal manager during the affected window are permanently locked in the contract. The corresponding underlying assets (ETH/LSTs) remain unredeemable in the unstaking vault. Users cannot recover their rsETH (it is held by the manager, not them) and cannot receive the underlying assets (the unlock step always reverts). This constitutes a permanent freeze of user funds.

**Impact rating: Critical — Permanent freezing of funds.**

### Likelihood Explanation

The admin legitimately needs to update the rsETH address during a token upgrade or migration. The protocol already has a `setRSETH` function that is expected to be called. There is no documentation warning against calling it while withdrawals are pending, and no on-chain enforcement. Any admin-initiated rsETH migration while the withdrawal queue is non-empty triggers the freeze. Given that the withdrawal queue is expected to be continuously active in production, the window of exposure is large.

### Recommendation

Add a guard in `setRSETH` that asserts the `LRTWithdrawalManager` holds zero balance of the current rsETH token before allowing the update:

```solidity
function setRSETH(address rsETH_) external onlyRole(DEFAULT_ADMIN_ROLE) {
    UtilLib.checkNonZeroAddress(rsETH_);
    address withdrawalManager = contractMap[LRTConstants.LRT_WITHDRAW_MANAGER];
    if (withdrawalManager != address(0)) {
        require(
            IERC20(rsETH).balanceOf(withdrawalManager) == 0,
            "LRTConfig: pending rsETH in withdrawal manager"
        );
    }
    rsETH = rsETH_;
    emit SetRSETH(rsETH_);
}
```

Alternatively, remove the ability to update `rsETH` after initialization, or require the withdrawal queue to be fully drained before the update is permitted.

### Proof of Concept

1. Alice calls `LRTWithdrawalManager.initiateWithdrawal(stETH, 10e18, "")`.
   - Line 166 transfers 10e18 of `rsETH_v1` tokens from Alice to the withdrawal manager.
   - A `WithdrawalRequest` is stored with `rsETHUnstaked = 10e18`.

2. Admin calls `LRTConfig.setRSETH(rsETH_v2)`.
   - `lrtConfig.rsETH()` now returns `rsETH_v2`.
   - The withdrawal manager still holds 10e18 of `rsETH_v1`.

3. Operator calls `LRTWithdrawalManager.unlockQueue(stETH, ...)`.
   - `_unlockWithdrawalRequests` accumulates `rsETHAmountToBurn = 10e18` and advances `nextLockedNonce`.
   - Line 305 calls `IRSETH(rsETH_v2).burnFrom(withdrawalManager, 10e18)`.
   - `rsETH_v2.balanceOf(withdrawalManager) == 0` → ERC-20 reverts.
   - The entire transaction reverts; `nextLockedNonce` is not persisted.

4. Every subsequent `unlockQueue` call hits the same revert. Alice's 10e18 `rsETH_v1` is permanently locked in the withdrawal manager, and the stETH in the unstaking vault is unreachable. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTConfig.sol (L215-219)
```text
    function setRSETH(address rsETH_) external onlyRole(DEFAULT_ADMIN_ROLE) {
        UtilLib.checkNonZeroAddress(rsETH_);
        rsETH = rsETH_;
        emit SetRSETH(rsETH_);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L166-166)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L301-305)
```text
        (rsETHBurned, assetAmountUnlocked) = _unlockWithdrawalRequests(
            asset, params.totalAvailableAssets, params.rsETHPrice, params.assetPrice, firstExcludedIndex
        );

        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
```

**File:** contracts/LRTWithdrawalManager.sol (L790-815)
```text
        while (nextLockedNonce_ < firstExcludedIndex) {
            bytes32 requestId = getRequestId(asset, nextLockedNonce_);
            WithdrawalRequest storage request = withdrawalRequests[requestId];

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

            // Calculate the amount user will receive
            uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);

            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request

            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
            assetAmountToUnlock += payoutAmount;

            unlockedWithdrawalsCount[asset]++;

            unchecked {
                nextLockedNonce_++;
            }
        }
        nextLockedNonce[asset] = nextLockedNonce_;
```
