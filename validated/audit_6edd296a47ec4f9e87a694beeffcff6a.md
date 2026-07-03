### Title
FIFO Withdrawal Queue Blocked by Oversized Withdrawal Request — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager.initiateWithdrawal` permits a user to commit up to the **total protocol assets** (including illiquid EigenLayer-staked assets) as their expected withdrawal amount. However, `unlockQueue` can only disburse assets that are **liquid in the `LRTUnstakingVault`**. Because `_unlockWithdrawalRequests` processes the queue in strict FIFO order and exits with `break` the moment the first pending request exceeds available liquid assets, a single oversized withdrawal request permanently stalls the queue for all subsequent users until the vault accumulates enough liquid assets to cover it.

---

### Finding Description

**Step 1 — Permissive submission check**

`initiateWithdrawal` validates the requested amount against `getAvailableAssetAmount`:

```solidity
// LRTWithdrawalManager.sol:170
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
```

`getAvailableAssetAmount` returns `totalAssets − assetsCommitted`, where `totalAssets` is sourced from `LRTDepositPool.getTotalAssetDeposits`:

```solidity
// LRTWithdrawalManager.sol:599-603
function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
    ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
    uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
    availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
}
```

`getTotalAssetDeposits` aggregates assets across the deposit pool, all NodeDelegators, EigenLayer strategies, and the unstaking vault — the vast majority of which are **illiquid** (staked in EigenLayer):

```solidity
// LRTDepositPool.sol:385-397
function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
    ...
    uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
    return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
            + assetLyingUnstakingVault);
}
```

**Step 2 — Liquid-only disbursement in `unlockQueue`**

`unlockQueue` passes only the vault's liquid balance as `totalAvailableAssets` to `_unlockWithdrawalRequests`. After unlocking, it calls `unstakingVault.redeem(asset, assetAmountUnlocked)`, which transfers actual tokens from the vault — confirming that only liquid vault assets are usable.

**Step 3 — FIFO `break` blocks the entire queue**

Inside `_unlockWithdrawalRequests`, the loop starts at `nextLockedNonce[asset]` and exits with `break` the moment the first pending request cannot be covered:

```solidity
// LRTWithdrawalManager.sol:790-800
while (nextLockedNonce_ < firstExcludedIndex) {
    ...
    // Check that the withdrawal delay has passed since the request's initiation.
    if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

    uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);

    if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request
    ...
}
```

The `firstExcludedIndex` parameter is an **upper** bound only; there is no mechanism for the operator to skip a blocking request and process later, smaller requests. `nextLockedNonce[asset]` is the immovable lower bound.

**Combined exploit**

Suppose the protocol holds 1 000 ETH total (100 ETH liquid in the vault, 900 ETH staked in EigenLayer):

| Step | Action | State |
|---|---|---|
| 1 | Attacker calls `initiateWithdrawal` for 1 000 ETH worth of rsETH | `assetsCommitted[ETH] = 1 000 ETH`; check passes because `totalAssets = 1 000 ETH` |
| 2 | Operator calls `unlockQueue` | `totalAvailableAssets = 100 ETH` (vault balance) |
| 3 | Loop hits attacker's request: `payoutAmount = 1 000 ETH > 100 ETH` | `break` — no requests unlocked |
| 4 | All subsequent users' requests remain locked | Queue frozen until vault accumulates 1 000 ETH |

After the attacker's request is eventually processed (once the vault is refilled via EigenLayer unstaking), the attacker can immediately submit a new oversized request to re-block the queue, sustaining the freeze at the cost of only the opportunity cost of their locked rsETH.

---

### Impact Explanation

All users whose withdrawal requests are queued **after** the attacker's request cannot complete their withdrawals. Their rsETH is already transferred to the `LRTWithdrawalManager` contract at `initiateWithdrawal` time and cannot be reclaimed. The freeze persists until the vault accumulates enough liquid assets to cover the blocking request, which may take days or weeks given EigenLayer's withdrawal delay. This constitutes **temporary freezing of funds** for an unbounded set of users.

Impact: **Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

The attack requires the attacker to hold rsETH and lock it in the withdrawal queue. The capital cost is non-trivial, but:

- The attacker eventually recovers their assets (just delayed), so the net cost is only the yield foregone during the lock period.
- The attack can be sustained indefinitely by re-submitting a new large request each time the previous one is processed.
- No privileged role is required; `initiateWithdrawal` is open to any rsETH holder.
- The mismatch between `getAvailableAssetAmount` (total protocol assets) and `totalAvailableAssets` (liquid vault balance) is a structural property of the protocol, not a transient condition.

Likelihood: **Medium.**

---

### Recommendation

1. **Replace `break` with `continue`** (or a skip mechanism) in `_unlockWithdrawalRequests` so that requests that cannot currently be covered are skipped rather than blocking the entire queue. This requires careful handling of `nextLockedNonce` to avoid permanently skipping requests.

2. **Cap `initiateWithdrawal` against liquid vault assets**, not total protocol assets. The submission check should use the vault's liquid balance (or a conservative fraction of it) rather than `getTotalAssetDeposits`, so that committed amounts are always coverable at unlock time.

3. **Allow the operator to specify a start index** in addition to `firstExcludedIndex`, enabling targeted processing of a sub-range of the queue and bypassing a stuck head request.

---

### Proof of Concept

```
Protocol state:
  totalAssets(ETH)       = 1 000 ETH  (100 liquid in vault, 900 in EigenLayer)
  assetsCommitted[ETH]   = 0

Attack:
  1. Attacker calls initiateWithdrawal(ETH, rsETHFor1000ETH, "")
     → expectedAssetAmount = 1 000 ETH
     → getAvailableAssetAmount() = 1 000 - 0 = 1 000 ETH  ✓ passes
     → assetsCommitted[ETH] = 1 000 ETH
     → request stored at nonce N

  2. Legitimate users submit withdrawal requests at nonces N+1, N+2, ...
     → getAvailableAssetAmount() = 1 000 - 1 000 = 0  (no capacity left)
     → their requests are blocked at submission too (bonus DoS)

  3. Operator calls unlockQueue(ETH, N+100, ...)
     → totalAvailableAssets = 100 ETH (vault balance)
     → loop starts at nextLockedNonce = N
     → payoutAmount for nonce N = 1 000 ETH
     → 100 < 1 000 → break
     → 0 requests unlocked

  4. Queue remains frozen. Users at N+1, N+2, ... cannot complete withdrawals.
     Their rsETH is locked in LRTWithdrawalManager with no recourse.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L162-178)
```text
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

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
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

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
    }
```
