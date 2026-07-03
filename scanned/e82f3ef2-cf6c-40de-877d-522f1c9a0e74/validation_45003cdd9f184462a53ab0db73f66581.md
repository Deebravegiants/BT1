### Title
Stale Pending Withdrawal State After `setRSETH()` Migration Permanently Freezes User rsETH — (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary
`LRTConfig.setRSETH()` allows the admin to replace the rsETH token address. `LRTWithdrawalManager` physically holds old rsETH tokens transferred from users during `initiateWithdrawal()`, and all downstream withdrawal-processing logic reads the rsETH address dynamically from `lrtConfig`. After a migration, the withdrawal manager holds old rsETH it can never burn, while `assetsCommitted` remains non-zero, permanently blocking both completion of existing requests and submission of new ones.

---

### Finding Description

`LRTConfig.setRSETH()` simply overwrites the stored address with no migration guard: [1](#0-0) 

`LRTWithdrawalManager.initiateWithdrawal()` transfers rsETH from the user into the withdrawal manager using the live `lrtConfig.rsETH()` value: [2](#0-1) 

After the transfer, the withdrawal manager accumulates state that is tightly coupled to the old rsETH token:

- Physical balance of old rsETH tokens held in the contract.
- `assetsCommitted[asset]` incremented to reflect the locked obligation.
- `withdrawalRequests`, `userAssociatedNonces`, and `nextUnusedNonce` entries keyed to the old rsETH-denominated amounts. [3](#0-2) 

When `setRSETH(newRsETH)` is called, `lrtConfig.rsETH()` immediately returns the new address. The `unlockQueue` path, which must burn rsETH held by the withdrawal manager, will now reference the new rsETH contract. The withdrawal manager holds zero balance of the new token, so the burn reverts. The old rsETH tokens are irrecoverable through any normal protocol flow.

Furthermore, `assetsCommitted[asset]` is never decremented for the stuck requests, so the `ExceedAmountToWithdraw` guard at line 170 blocks all subsequent `initiateWithdrawal` calls for the same asset: [4](#0-3) 

This is structurally identical to the external report: the minter's `collectionIdToAllowList` mapping remained bound to the old NFT contract after `fantiumNFTContractAddress` was replaced. Here, the withdrawal manager's committed-asset accounting and physical rsETH balance remain bound to the old rsETH contract after `setRSETH()` is called.

---

### Impact Explanation

Every user who called `initiateWithdrawal()` before the migration has their rsETH permanently frozen inside `LRTWithdrawalManager`. The tokens cannot be burned (wrong contract), cannot be returned (no recovery path), and the `assetsCommitted` accounting prevents new users from withdrawing the same asset. This is a **permanent freezing of user funds** — Critical severity.

---

### Likelihood Explanation

`setRSETH()` is a supported, non-deprecated admin function with no precondition checks. A legitimate upgrade of the rsETH token contract (e.g., adding new functionality, fixing a bug in the token itself) would trigger this path. No malicious intent is required; the damage occurs as a side-effect of a routine governance action, exactly as in the referenced report.

---

### Recommendation

1. **Guard `setRSETH()` with a migration precondition**: revert if any asset has `assetsCommitted[asset] > 0` or if `nextUnusedNonce[asset] > nextLockedNonce[asset]` for any asset, ensuring no pending requests exist before the address is swapped.
2. **Snapshot the rsETH address per request**: store the rsETH address at the time `initiateWithdrawal()` is called inside `WithdrawalRequest`, so the correct token is always used for burning regardless of future config changes.
3. **Remove `setRSETH()` entirely**: rely on proxy upgrades of the rsETH contract rather than address replacement, eliminating the migration surface.

---

### Proof of Concept

1. User calls `LRTWithdrawalManager.initiateWithdrawal(stETH, 1e18, "")`.
   - `IERC20(lrtConfig.rsETH()).safeTransferFrom(user, withdrawalManager, 1e18)` — old rsETH now held by the manager.
   - `assetsCommitted[stETH] += expectedStETH`.
2. Admin calls `LRTConfig.setRSETH(newRsETH)`.
   - `lrtConfig.rsETH()` now returns `newRsETH`.
3. Operator calls `LRTWithdrawalManager.unlockQueue(stETH, ...)`.
   - Internally attempts to burn rsETH via `lrtConfig.rsETH()` → targets `newRsETH`.
   - `newRsETH.balanceOf(withdrawalManager) == 0` → burn reverts → `unlockQueue` reverts.
4. User calls `completeWithdrawal(stETH, "")` → reverts because the request was never unlocked.
5. User's 1e18 old rsETH is permanently frozen in `LRTWithdrawalManager`.
6. `assetsCommitted[stETH]` remains elevated, causing all future `initiateWithdrawal` calls for stETH to revert with `ExceedAmountToWithdraw`. [1](#0-0) [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/LRTConfig.sol (L215-219)
```text
    function setRSETH(address rsETH_) external onlyRole(DEFAULT_ADMIN_ROLE) {
        UtilLib.checkNonZeroAddress(rsETH_);
        rsETH = rsETH_;
        emit SetRSETH(rsETH_);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L35-58)
```text
    mapping(address asset => uint256) public minRsEthAmountToWithdraw;
    uint256 public withdrawalDelayBlocks;

    // Next available nonce for withdrawal requests per asset, indicating total requests made.
    mapping(address asset => uint256 nonce) public nextUnusedNonce;

    // Next nonce for which a withdrawal request remains locked.
    mapping(address asset => uint256 requestNonce) public nextLockedNonce;

    // Mapping from a unique request identifier to its corresponding withdrawal request
    mapping(bytes32 requestId => WithdrawalRequest) public withdrawalRequests;

    // Maps each asset to user addresses, pointing to an ordered list of their withdrawal request nonces.
    // Utilizes a double-ended queue for efficient management and removal of initial requests.
    mapping(address asset => mapping(address user => DoubleEndedQueue.Uint256Deque requestNonces)) public
        userAssociatedNonces;

    // Asset amount committed to be withdrawn by users.
    mapping(address asset => uint256 amount) public assetsCommitted;

    mapping(address asset => bool) public isInstantWithdrawalEnabled;
    uint256 public instantWithdrawalFee; // Fee in basis points (1 = 0.01%)

    mapping(address asset => uint256) public unlockedWithdrawalsCount;
```

**File:** contracts/LRTWithdrawalManager.sol (L162-177)
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
```

**File:** contracts/LRTWithdrawalManager.sol (L268-284)
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
    {
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
```
