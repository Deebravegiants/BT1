### Title
No Mechanism to Cancel Queued Withdrawal Requests When Paused — (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager` has no function to cancel or remove a queued withdrawal request. When the contract is paused, users' rsETH is locked inside the contract with no recovery path: `completeWithdrawal`, `completeWithdrawalForUser`, and `unlockQueue` are all gated by `whenNotPaused`, and no admin-callable removal function exists. This is the direct analog of the reported "No way of removing Fraudulent Roots" pattern: a queue whose entries cannot be purged even when the protocol is halted.

---

### Finding Description

`initiateWithdrawal` transfers the caller's rsETH into the contract and appends a `WithdrawalRequest` to the per-asset queue:

```solidity
// LRTWithdrawalManager.sol L166-175
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
...
assetsCommitted[asset] += expectedAssetAmount;
_addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
``` [1](#0-0) 

Every downstream path that could return funds or process the request is blocked while paused:

| Function | Guard |
|---|---|
| `completeWithdrawal` | `whenNotPaused` |
| `completeWithdrawalForUser` | `whenNotPaused` |
| `unlockQueue` | `whenNotPaused` | [2](#0-1) [3](#0-2) 

There is no `cancelWithdrawal`, no admin-callable removal function, and no emergency rsETH-return path anywhere in the contract or its interface. [4](#0-3) 

The `_addUserWithdrawalRequest` internal function stores the request and increments `nextUnusedNonce` but provides no inverse operation: [5](#0-4) 

---

### Impact Explanation

Any rsETH deposited into `LRTWithdrawalManager` via `initiateWithdrawal` before a pause event is frozen for the entire duration of the pause. Because `LRTConfig.pauseAll()` pauses `LRTWithdrawalManager` alongside all other protocol contracts in a single call, a broad security pause immediately traps all in-flight withdrawal rsETH with no admin escape hatch. [6](#0-5) 

**Impact class**: Medium — Temporary freezing of user funds (rsETH held in `LRTWithdrawalManager`).

---

### Likelihood Explanation

The `PAUSER_ROLE` can pause the contract at any time in response to a real or perceived security event. Users who have already called `initiateWithdrawal` have no way to anticipate or avoid the freeze. The scenario is realistic: pauses are a normal incident-response action, and the window between a user queuing a withdrawal and the pause being lifted can be arbitrarily long.

---

### Recommendation

Add a `cancelWithdrawal(address asset)` function that:
1. Is callable by the requesting user even when the contract is paused (`whenPaused` or no pause guard).
2. Pops the user's oldest pending (still-locked) nonce from `userAssociatedNonces[asset][msg.sender]`.
3. Deletes the corresponding `withdrawalRequests` entry.
4. Decreases `assetsCommitted[asset]` by `request.expectedAssetAmount`.
5. Returns `request.rsETHUnstaked` rsETH to the user.

Alternatively, add an admin-only emergency function (callable only when paused) that can remove a specific queued request and return the rsETH to the original requester, mirroring the recommendation in the referenced report.

---

### Proof of Concept

1. Alice calls `initiateWithdrawal(stETH, 1e18 rsETH, "")`.
   - `1e18` rsETH is transferred from Alice to `LRTWithdrawalManager`. [7](#0-6) 
   - `assetsCommitted[stETH] += expectedAmount`. [8](#0-7) 
   - Request stored at nonce `N`. [9](#0-8) 

2. `PAUSER_ROLE` calls `LRTConfig.pauseAll()`, pausing `LRTWithdrawalManager`. [10](#0-9) 

3. Alice attempts `completeWithdrawal(stETH, "")` → reverts: `Pausable: paused`. [2](#0-1) 

4. Operator attempts `unlockQueue(stETH, ...)` → reverts: `Pausable: paused`. [11](#0-10) 

5. No `cancelWithdrawal` exists. Alice's `1e18` rsETH remains locked in the contract for the entire duration of the pause with no recovery path.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L166-175)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L183-184)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
```

**File:** contracts/LRTWithdrawalManager.sol (L268-281)
```text
    function unlockQueue(
        address asset,
        uint256 firstExcludedIndex,
        uint256 minimumAssetPrice,
        uint256 minimumRsEthPrice,
        uint256 maximumAssetPrice,
        uint256 maximumRsEthPrice
    )
        external
        nonReentrant
        onlySupportedAsset(asset)
        whenNotPaused
        onlyAssetTransferOrOperatorRole
        returns (uint256 rsETHBurned, uint256 assetAmountUnlocked)
```

**File:** contracts/LRTWithdrawalManager.sol (L744-758)
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

```

**File:** contracts/interfaces/ILRTWithdrawalManager.sol (L80-149)
```text
    // methods
    function getExpectedAssetAmount(address asset, uint256 amount) external view returns (uint256);

    function getAvailableAssetAmount(address asset) external view returns (uint256 assetAmount);

    function getUserWithdrawalRequest(
        address asset,
        address user,
        uint256 index
    )
        external
        view
        returns (uint256 rsETHAmount, uint256 expectedAssetAmount, uint256 withdrawalStartBlock, uint256 userNonce);

    function initiateWithdrawal(address asset, uint256 withdrawAmount, string calldata referralId) external;

    function completeWithdrawal(address asset, string calldata referralId) external;

    function completeWithdrawalForUser(address asset, address user, string calldata referralId) external;

    function unlockQueue(
        address asset,
        uint256 index,
        uint256 minimumAssetPrice,
        uint256 minimumRsEthPrice,
        uint256 maximumAssetPrice,
        uint256 maximumRsEthPrice
    )
        external
        returns (uint256 rsETHBurned, uint256 assetAmountUnlocked);

    // receive functions
    function receiveFromLRTUnstakingVault() external payable;

    function setInstantWithdrawalEnabled(address asset, bool enabled) external;

    function setInstantWithdrawalFee(uint256 feeBasisPoints) external;

    function setInstantWithdrawalFeeRecipient(address feeRecipient) external;

    function assetsCommitted(address asset) external view returns (uint256);

    // Treasury withdrawal flow functions
    function hasUnlockedWithdrawals(address asset) external view returns (bool);

    function sweepRemainingAssets(address asset) external returns (uint256 transferredAmount);

    // Aave integration functions
    function configureAaveIntegration(
        address aavePool_,
        address aaveWETHGateway_,
        address aaveAWETH_,
        address aaveDataProvider_
    )
        external;

    function setAaveIntegrationEnabled(bool enabled) external;

    function depositIdleETHToAave(uint256 amount) external;

    function collectInterestToTreasury() external returns (uint256 interestAmount);

    function emergencyWithdrawFromAave(uint256 amount) external;

    function getAaveBalance() external view returns (uint256);

    function getAccruedInterest() external view returns (uint256);

    function aaveHealthCheck() external view returns (bool);
}
```

**File:** contracts/LRTConfig.sol (L262-285)
```text
    function pauseAll() external onlyRole(LRTConstants.PAUSER_ROLE) {
        IPausable lrtDepositPool = IPausable(getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable lrtWithdrawalManager = IPausable(getContract(LRTConstants.LRT_WITHDRAW_MANAGER));
        IPausable lrtOracle = IPausable(getContract(LRTConstants.LRT_ORACLE));
        IPausable rsETHContract = IPausable(rsETH);

        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!lrtWithdrawalManager.paused()) lrtWithdrawalManager.pause();
        if (!lrtOracle.paused()) lrtOracle.pause();
        if (!rsETHContract.paused()) rsETHContract.pause();

        address[] memory nodeDelegatorQueue = ILRTDepositPool(address(lrtDepositPool)).getNodeDelegatorQueue();
        uint256 nodeDelegatorCount = nodeDelegatorQueue.length;

        for (uint256 i = 0; i < nodeDelegatorCount;) {
            IPausable nodeDelegator = IPausable(nodeDelegatorQueue[i]);
            if (!nodeDelegator.paused()) nodeDelegator.pause();
            unchecked {
                ++i;
            }
        }

        emit PausedAll(msg.sender);
    }
```
