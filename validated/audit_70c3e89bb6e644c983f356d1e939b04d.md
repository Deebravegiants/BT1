### Title
Unbounded Withdrawal Requests Allow Attacker to Commit All Available Assets, Temporarily Freezing Withdrawal Initiation for Other Users - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager.initiateWithdrawal` imposes no per-user limit on the number of active withdrawal requests. Any rsETH holder can create an unbounded number of minimum-amount requests, each of which increments the global `assetsCommitted[asset]` counter. Once the committed amount equals total available assets, `getAvailableAssetAmount` returns zero and every subsequent `initiateWithdrawal` call from any user reverts with `ExceedAmountToWithdraw`, temporarily freezing withdrawal initiation for all other users.

---

### Finding Description

`initiateWithdrawal` enforces two checks before queuing a request:

```solidity
// contracts/LRTWithdrawalManager.sol
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
...
uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
assetsCommitted[asset] += expectedAssetAmount;
_addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
``` [1](#0-0) 

`getAvailableAssetAmount` is computed as:

```solidity
availableAssetAmount = totalAssets > assetsCommitted[asset]
    ? totalAssets - assetsCommitted[asset]
    : 0;
``` [2](#0-1) 

There is **no cap on the number of requests a single user may hold**. An attacker who holds enough rsETH can call `initiateWithdrawal` repeatedly with the minimum allowed amount, each time incrementing `assetsCommitted[asset]`. Once `assetsCommitted[asset]` reaches `totalAssets`, `getAvailableAssetAmount` returns 0 and every other user's `initiateWithdrawal` reverts.

The global withdrawal queue (`nextUnusedNonce[asset]`) grows without bound, and the attacker's requests are placed ahead of all future legitimate requests in the FIFO queue processed by `_unlockWithdrawalRequests`:

```solidity
while (nextLockedNonce_ < firstExcludedIndex) {
    ...
    if (availableAssetAmount < payoutAmount) break;
    ...
    nextLockedNonce_++;
}
``` [3](#0-2) 

The attacker's requests must be processed first (FIFO) before the operator can unlock legitimate users' requests. During the mandatory `withdrawalDelayBlocks` (default 8 days), all assets remain committed to the attacker's requests.

---

### Impact Explanation

**Temporary freezing of funds (Medium).** During the attack window (up to 8 days per cycle), no other user can call `initiateWithdrawal` for the affected asset. Legitimate users' rsETH is not stolen, but their ability to initiate the withdrawal lifecycle is completely blocked. The attacker recovers their rsETH-equivalent assets after the delay and can repeat the attack indefinitely, creating a sustained denial-of-service on the withdrawal queue.

---

### Likelihood Explanation

**Medium.** The attacker must hold enough rsETH to commit all available assets in the `LRTUnstakingVault`. On L2 deployments (Arbitrum, Optimism, Unichain) where gas fees are negligible, the cost of creating thousands of minimum-amount requests is low. The attacker's capital is returned after the delay, so the net cost is only the opportunity cost of locking rsETH for 8 days. A well-capitalised adversary (e.g., a competing protocol or a large rsETH holder) can sustain this attack cheaply on low-fee chains.

---

### Recommendation

Add a per-user cap on the number of active (unlocked) withdrawal requests:

```solidity
uint256 public maxWithdrawalRequestsPerUser; // e.g., 10

function initiateWithdrawal(...) external {
    require(
        userAssociatedNonces[asset][msg.sender].length() < maxWithdrawalRequestsPerUser,
        "TooManyActiveRequests"
    );
    ...
}
```

This mirrors the fix applied in the referenced Llama report, which removed the unbounded-growth vector by adding a structural cap. Alternatively, require a non-trivial minimum withdrawal amount large enough to make mass-request flooding economically infeasible.

---

### Proof of Concept

1. Protocol has `X` ETH available for withdrawal (`getAvailableAssetAmount(ETH_TOKEN) == X`).
2. Attacker holds rsETH worth `X` ETH at current oracle price.
3. Attacker calls `initiateWithdrawal(ETH_TOKEN, minRsEthAmountToWithdraw[ETH_TOKEN], "")` in a loop, N times, where `N * minExpectedAsset ≈ X`.
4. After N calls, `assetsCommitted[ETH_TOKEN] == X`, so `getAvailableAssetAmount` returns 0.
5. Any honest user calling `initiateWithdrawal` now reverts with `ExceedAmountToWithdraw`.
6. The operator calls `unlockQueue` in batches; the attacker's N requests are processed first (FIFO), consuming all unlocked assets.
7. After `withdrawalDelayBlocks` (~8 days), attacker calls `completeWithdrawal` N times and recovers all assets.
8. Attacker repeats from step 2. [4](#0-3) [5](#0-4)

### Citations

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

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L744-759)
```text
    function _addUserWithdrawalRequest(address asset, uint256 rsETHUnstaked, uint256 expectedAssetAmount) internal {
        uint256 nextUnusedNonce_ = nextUnusedNonce[asset];

        // Generate a unique identifier for the new withdrawal request.
        bytes32 requestId = getRequestId(asset, nextUnusedNonce_);

        // Create and store the new withdrawal request.
        withdrawalRequests[requestId] = WithdrawalRequest({
            rsETHUnstaked: rsETHUnstaked, expectedAssetAmount: expectedAssetAmount, withdrawalStartBlock: block.number
        });

        // Map the user to the newly created request index and increment the nonce for future requests.
        userAssociatedNonces[asset][msg.sender].pushBack(nextUnusedNonce_);
        nextUnusedNonce[asset] = nextUnusedNonce_ + 1;

        emit AssetWithdrawalQueued(msg.sender, asset, rsETHUnstaked, nextUnusedNonce_);
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
