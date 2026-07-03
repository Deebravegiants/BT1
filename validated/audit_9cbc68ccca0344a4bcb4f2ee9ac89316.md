### Title
Blocked rsETH Holders Cannot Initiate Withdrawals, Temporarily Freezing Their Funds - (File: contracts/RSETH.sol)

### Summary
`RSETH._transfer` enforces a transfer block on both `from` and `to` addresses. When a user is blocked via `blockUserTransfers`, they cannot call `LRTWithdrawalManager.initiateWithdrawal` or `instantWithdrawal`, because both paths internally invoke `_transfer` (or `burnFrom`) on the blocked user's address, causing a revert. The user's rsETH is frozen for the duration of the block with no self-service recovery path.

### Finding Description
`RSETH._transfer` overrides the ERC-20 `_transfer` to call `_enforceNotBlocked` on both `from` and `to`:

```solidity
// contracts/RSETH.sol L287-291
function _transfer(address from, address to, uint256 amount) internal override {
    _enforceNotBlocked(from);
    _enforceNotBlocked(to);
    super._transfer(from, to, amount);
}
```

`_enforceNotBlocked` reverts with `TransfersBlocked` if `block.timestamp < transfersBlockedUntil[account]` and the account is not permanently exempt.

`LRTWithdrawalManager.initiateWithdrawal` pulls rsETH from the caller:

```solidity
// contracts/LRTWithdrawalManager.sol L166
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

This resolves to `RSETH._transfer(msg.sender, address(LRTWithdrawalManager), rsETHUnstaked)`, which calls `_enforceNotBlocked(msg.sender)`. If the user is blocked, this reverts.

`instantWithdrawal` calls `RSETH.burnFrom(address(msg.sender), rsETHUnstaked)`:

```solidity
// contracts/RSETH.sol L245-248
function burnFrom(address account, uint256 amount) external onlyRole(LRTConstants.BURNER_ROLE) whenNotPaused {
    _enforceNotBlocked(account);
    _burn(account, amount);
}
```

This also reverts for a blocked user.

The only admin-side recovery path is `recoverFrozenFunds`, which transfers the user's entire balance to `custodyAddress` — not back to the user. There is no mechanism for a blocked user to self-service exit their position.

### Impact Explanation
A blocked rsETH holder cannot:
- Call `initiateWithdrawal` to queue rsETH for LST/ETH redemption.
- Call `instantWithdrawal` to immediately redeem rsETH.

Their rsETH is frozen for the duration of the block (up to 24 hours per application). The block can be re-applied before expiry, refreshing the hold. The only admin recovery path (`recoverFrozenFunds`) confiscates funds to `custodyAddress`, not to the user. This constitutes **temporary freezing of funds** (Medium impact per scope).

### Likelihood Explanation
`blockUserTransfers` is callable by `onlyLRTManager` — a role that exists and is exercised in normal protocol operations (e.g., compliance holds, suspicious activity). The block is a legitimate feature, but its side effect of preventing withdrawals is unintended. Any time a manager legitimately blocks a user who holds rsETH, that user's withdrawal path is severed for the block duration.

### Recommendation
Exclude the `LRTWithdrawalManager` address (and any other trusted protocol contract acting as `to`) from the `_enforceNotBlocked(to)` check in `_transfer`. Alternatively, add a dedicated withdrawal path in `RSETH` that bypasses the block check when the destination is a known protocol contract, analogous to how `recoverFrozenFunds` calls `super._transfer` directly to bypass the override.

### Proof of Concept

1. User holds 10 rsETH.
2. LRT Manager calls `RSETH.blockUserTransfers([user])`, setting `transfersBlockedUntil[user] = block.timestamp + 1 days`.
3. User calls `LRTWithdrawalManager.initiateWithdrawal(asset, 10e18, "")`.
4. Internally: `IERC20(rsETH).safeTransferFrom(user, address(withdrawalManager), 10e18)` → `RSETH._transfer(user, withdrawalManager, 10e18)` → `_enforceNotBlocked(user)` → reverts with `TransfersBlocked`.
5. User calls `LRTWithdrawalManager.instantWithdrawal(asset, 10e18, "")`.
6. Internally: `RSETH.burnFrom(user, 10e18)` → `_enforceNotBlocked(user)` → reverts with `TransfersBlocked`.
7. User's 10 rsETH is inaccessible for up to 24 hours. If the manager re-applies the block before expiry, the freeze extends indefinitely. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** contracts/RSETH.sol (L245-248)
```text
    function burnFrom(address account, uint256 amount) external onlyRole(LRTConstants.BURNER_ROLE) whenNotPaused {
        _enforceNotBlocked(account);
        _burn(account, amount);
    }
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

**File:** contracts/LRTWithdrawalManager.sol (L161-178)
```text
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

**File:** contracts/LRTWithdrawalManager.sol (L212-253)
```text
    function instantWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
        onlyInstantWithdrawalAllowed(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
        if (IERC20(lrtConfig.rsETH()).balanceOf(msg.sender) < rsETHUnstaked) revert NotEnoughRsETH();
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);

        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;

        address feeRecipient = instantWithdrawalFeeRecipient;
        if (feeRecipient == address(0)) {
            // Backwards-compatible default: send fees to the protocol treasury
            feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        }
        if (fee > 0) {
            _transferAsset(asset, feeRecipient, fee);
            emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
        }

        _transferAsset(asset, msg.sender, userAmount);
        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(msg.sender, asset, rsETHUnstaked, userAmount);
    }
```
