### Title
Replacing `LRTWithdrawalManager` via `LRTConfig.setContract` permanently freezes pending withdrawal rsETH - (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTConfig.setContract` allows `DEFAULT_ADMIN_ROLE` to replace the `LRT_WITHDRAW_MANAGER` address with a freshly deployed `LRTWithdrawalManager`. The new contract initializes all nonce counters at zero and holds no withdrawal state. Users who called `initiateWithdrawal` on the old contract already transferred their rsETH into it; because the `unlockQueue` operator flow migrates to the new contract, the old contract's `nextLockedNonce` is never advanced, and those users can never call `completeWithdrawal` successfully. Their rsETH is permanently frozen.

---

### Finding Description

**Step 1 – User initiates a withdrawal on the current `LRTWithdrawalManager`.**

`initiateWithdrawal` transfers rsETH from the user into the contract and records the request under a per-asset nonce:

```solidity
// contracts/LRTWithdrawalManager.sol
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
...
_addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
``` [1](#0-0) 

Inside `_addUserWithdrawalRequest`, the request is stored under `nextUnusedNonce[asset]` and the nonce is incremented:

```solidity
uint256 nextUnusedNonce_ = nextUnusedNonce[asset];
bytes32 requestId = getRequestId(asset, nextUnusedNonce_);
withdrawalRequests[requestId] = WithdrawalRequest({...});
userAssociatedNonces[asset][msg.sender].pushBack(nextUnusedNonce_);
nextUnusedNonce[asset] = nextUnusedNonce_ + 1;
``` [2](#0-1) 

**Step 2 – Governance deploys a new `LRTWithdrawalManager` and calls `LRTConfig.setContract`.**

`setContract` has no guard against replacing the withdrawal manager while pending requests exist:

```solidity
function setContract(bytes32 contractKey, address contractAddress) external onlyRole(DEFAULT_ADMIN_ROLE) {
    _setContract(contractKey, contractAddress);
}
``` [3](#0-2) 

The new contract's `initialize` sets all state to zero:

```solidity
function initialize(address lrtConfigAddr) external initializer {
    ...
    withdrawalDelayBlocks = 8 days / 12 seconds;
    lrtConfig = ILRTConfig(lrtConfigAddr);
}
``` [4](#0-3) 

After this call, `nextUnusedNonce[asset] = 0`, `nextLockedNonce[asset] = 0`, and `withdrawalRequests` is empty in the new contract.

**Step 3 – The old contract's `unlockQueue` is never called again.**

`unlockQueue` is restricted to `onlyAssetTransferOrOperatorRole`. Operators will direct all future `unlockQueue` calls to the new contract. The old contract's `nextLockedNonce[asset]` is frozen at whatever value it had at upgrade time.

```solidity
function unlockQueue(...) external nonReentrant onlySupportedAsset(asset) whenNotPaused onlyAssetTransferOrOperatorRole ...
``` [5](#0-4) 

**Step 4 – Users with pending requests on the old contract can never complete withdrawal.**

`_processWithdrawalCompletion` enforces:

```solidity
if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
``` [6](#0-5) 

Because `nextLockedNonce[asset]` on the old contract is never advanced past its upgrade-time value, every user whose nonce was not yet unlocked at upgrade time will always hit `WithdrawalLocked`. Their rsETH, already transferred into the old contract, is permanently inaccessible.

---

### Impact Explanation

**Permanent freezing of user funds (Critical).** rsETH transferred by users during `initiateWithdrawal` is held by the old `LRTWithdrawalManager` contract. After the address is replaced in `LRTConfig`, the unlock path for those requests is severed: operators use the new contract, the old contract's `nextLockedNonce` never advances, and `completeWithdrawal` on the old contract always reverts with `WithdrawalLocked`. There is no escape hatch or sweep function for users.

---

### Likelihood Explanation

**Medium.** Replacing the withdrawal manager is a plausible governance action when deploying an upgraded version of the contract. The protocol already has precedent for this pattern (`initialize2`, `initialize3` reinitializers show iterative upgrades). A governance team unaware of the state-migration requirement would naturally deploy a new contract and call `setContract`, triggering the freeze for all users with in-flight withdrawal requests at that moment.

---

### Recommendation

1. **Add a migration initializer** to any new `LRTWithdrawalManager` deployment that accepts the final `nextUnusedNonce[asset]` and `nextLockedNonce[asset]` values from the old contract, mirroring the `initialize2`/`initialize3` pattern already used for `unlockedWithdrawalsCount`.
2. **Guard `setContract` for `LRT_WITHDRAW_MANAGER`**: revert if `nextUnusedNonce[asset] > nextLockedNonce[asset]` for any supported asset (i.e., pending requests exist).
3. Alternatively, always upgrade the existing proxy in place rather than deploying a new contract, so storage is preserved.

---

### Proof of Concept

```
1. Alice calls initiateWithdrawal(stETH, 10e18, "ref")
   → 10e18 rsETH transferred to old LRTWithdrawalManager
   → withdrawal stored at nonce 42; nextUnusedNonce[stETH] = 43

2. Governance deploys new LRTWithdrawalManager (nextUnusedNonce = 0, nextLockedNonce = 0)
   → LRTConfig.setContract(LRT_WITHDRAW_MANAGER, newAddress)

3. Operator calls unlockQueue(...) on NEW contract → no effect on old contract state

4. Alice calls completeWithdrawal(stETH, "ref") on OLD contract
   → usersFirstWithdrawalRequestNonce = 42
   → nextLockedNonce[stETH] on old contract = (frozen value, e.g. 40)
   → 42 >= 40 → revert WithdrawalLocked()

5. Alice's 10e18 rsETH is permanently locked in the old contract.
   No admin function exists to recover it for her.
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L90-98)
```text
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        __Pausable_init();
        __ReentrancyGuard_init();
        withdrawalDelayBlocks = 8 days / 12 seconds;

        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L166-175)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
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

**File:** contracts/LRTWithdrawalManager.sol (L705-707)
```text
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
```

**File:** contracts/LRTWithdrawalManager.sol (L744-757)
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

**File:** contracts/LRTConfig.sol (L237-239)
```text
    function setContract(bytes32 contractKey, address contractAddress) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _setContract(contractKey, contractAddress);
    }
```
