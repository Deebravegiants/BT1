### Title
FIFO Withdrawal Queue Blocked by Oversized Requests Freezes Subsequent User Withdrawals - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`_unlockWithdrawalRequests` processes the withdrawal queue in strict FIFO order and unconditionally `break`s when a single request's payout exceeds available vault assets. Any withdrawal request that cannot be immediately covered halts processing of all subsequent requests, regardless of their size, temporarily freezing funds for every user queued behind the blocking request.

### Finding Description
`LRTWithdrawalManager.unlockQueue` calls `_unlockWithdrawalRequests`, which iterates from `nextLockedNonce[asset]` up to `firstExcludedIndex` in sequential order. At line 800, when the vault's available balance is insufficient to cover the front-of-queue request, the loop exits immediately:

```solidity
if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request
```

There is no mechanism to skip the blocking request and continue processing smaller requests behind it. The `firstExcludedIndex` parameter only sets an upper bound on which requests to consider; it cannot be used to skip the request at `nextLockedNonce[asset]` because line 788 reverts if `nextLockedNonce_ >= firstExcludedIndex`:

```solidity
if (nextLockedNonce_ >= firstExcludedIndex) revert NoPendingWithdrawals();
```

The available asset amount used during unlock (`unstakingVault.balanceOf(asset)`, line 849) reflects only the current balance of the `LRTUnstakingVault`, which is typically a small fraction of total protocol TVL (most assets reside in EigenLayer strategies). Meanwhile, `initiateWithdrawal` permits queuing requests up to `getAvailableAssetAmount`, which accounts for the full protocol TVL including EigenLayer-held assets (line 601: `lrtDepositPool.getTotalAssetDeposits(asset)`). This structural gap means a legitimately queued large withdrawal can sit at the front of the queue with a `payoutAmount` that far exceeds the vault's current liquid balance, blocking all subsequent requests indefinitely until operators manually unstake from EigenLayer and replenish the vault.

### Impact Explanation
Every user whose withdrawal request is queued after a large blocking request has their rsETH locked in the `LRTWithdrawalManager` contract (transferred in at `initiateWithdrawal`, line 166) and cannot complete their withdrawal. The delay is bounded only by how long it takes operators to unstake from EigenLayer (subject to EigenLayer's withdrawal delay, typically 7+ days) and replenish the vault. This constitutes a temporary freeze of user funds.

**Impact: Medium — Temporary freezing of funds.**

### Likelihood Explanation
The condition is reachable by any user who calls `initiateWithdrawal` with a large rsETH amount. Because `getAvailableAssetAmount` counts EigenLayer-held assets while `unlockQueue` only sees the vault's liquid balance, the gap is structural and persistent. A single whale withdrawal request is sufficient to block the entire queue for all subsequent users. No privileged access or special conditions are required beyond holding a large rsETH balance.

**Likelihood: Medium.**

### Recommendation
Implement a skip-and-continue mechanism in `_unlockWithdrawalRequests` so that when a request cannot be covered by current vault liquidity, the loop continues to evaluate subsequent requests rather than breaking. Alternatively, allow operators to mark specific nonces as "deferred" so the queue pointer can advance past them. This mirrors the partial-liquidation fix recommended in the reference report: allow the system to make progress on what it *can* cover rather than halting entirely on what it cannot.

### Proof of Concept

1. Protocol TVL: 10,000 ETH in EigenLayer, 100 ETH in `LRTUnstakingVault`.
2. Alice calls `initiateWithdrawal(ETH, rsETH_for_500_ETH, ...)`. `getAvailableAssetAmount` returns 10,000 ETH (full TVL), so the check at line 170 passes. Alice's request is queued at nonce 0 with `expectedAssetAmount = 500 ETH`.
3. Bob calls `initiateWithdrawal(ETH, rsETH_for_1_ETH, ...)`. Bob's request is queued at nonce 1 with `expectedAssetAmount = 1 ETH`.
4. Operator calls `unlockQueue(ETH, 2, ...)`. `_createUnlockParams` sets `totalAvailableAssets = 100 ETH` (vault balance).
5. Loop iteration 1 (nonce 0): `payoutAmount = 500 ETH`, `availableAssetAmount = 100 ETH`. Condition at line 800 triggers: `break`.
6. `nextLockedNonce[ETH]` remains 0. Bob's 1 ETH request (nonce 1) is never evaluated.
7. Bob's rsETH remains locked in `LRTWithdrawalManager`. Bob cannot complete his withdrawal until operators unstake 400+ ETH from EigenLayer (7+ day delay) and replenish the vault. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L162-170)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
```

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L786-788)
```text
        uint256 nextLockedNonce_ = nextLockedNonce[asset];
        // Revert when trying to unlock a request that has already been unlocked
        if (nextLockedNonce_ >= firstExcludedIndex) revert NoPendingWithdrawals();
```

**File:** contracts/LRTWithdrawalManager.sol (L790-800)
```text
        while (nextLockedNonce_ < firstExcludedIndex) {
            bytes32 requestId = getRequestId(asset, nextLockedNonce_);
            WithdrawalRequest storage request = withdrawalRequests[requestId];

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

            // Calculate the amount user will receive
            uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);

            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request
```

**File:** contracts/LRTWithdrawalManager.sol (L846-850)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
```
