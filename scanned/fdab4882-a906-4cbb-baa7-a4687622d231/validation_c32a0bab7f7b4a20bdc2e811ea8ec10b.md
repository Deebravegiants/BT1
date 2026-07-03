### Title
`setMinRsEthAmountToWithdraw` Has No Upper Bound, Enabling Implicit Withdrawal Initiation Lock — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager.setMinRsEthAmountToWithdraw` accepts any `uint256` value with no upper-bound validation. If the LRT admin sets `minRsEthAmountToWithdraw[asset]` to an arbitrarily large value (e.g., `type(uint256).max`), every call to `initiateWithdrawal` and `instantWithdrawal` for that asset will revert, creating an implicit, protocol-wide withdrawal initiation lock with no explicit on-chain signal that a lock is in effect.

---

### Finding Description

`setMinRsEthAmountToWithdraw` in `LRTWithdrawalManager.sol` sets the per-asset minimum rsETH amount required to open a withdrawal request:

```solidity
// contracts/LRTWithdrawalManager.sol L330-333
function setMinRsEthAmountToWithdraw(address asset, uint256 minRsEthAmountToWithdraw_) external onlyLRTAdmin {
    minRsEthAmountToWithdraw[asset] = minRsEthAmountToWithdraw_;
    emit MinAmountToWithdrawUpdated(asset, minRsEthAmountToWithdraw_);
}
```

There is no upper-bound check. Both user-facing withdrawal entry points enforce this minimum:

```solidity
// contracts/LRTWithdrawalManager.sol L162-164
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
```

The identical guard appears in `instantWithdrawal` at line 224. If `minRsEthAmountToWithdraw[asset]` is set to `type(uint256).max`, the condition `rsETHUnstaked < type(uint256).max` is always true for any realistic rsETH balance, so every call to `initiateWithdrawal` and `instantWithdrawal` reverts. No user can queue a new withdrawal for that asset.

Contrast this with `setWithdrawalDelayBlocks`, which does enforce an upper bound:

```solidity
// contracts/LRTWithdrawalManager.sol L338-343
function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
    if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();
    withdrawalDelayBlocks = withdrawalDelayBlocks_;
    ...
}
```

`setMinRsEthAmountToWithdraw` has no equivalent guard, making the implicit lock unbounded.

---

### Impact Explanation

All rsETH holders wishing to redeem their tokens for the affected underlying asset (ETH, stETH, ETHx, etc.) are unable to initiate new withdrawal requests. Users who have already queued requests before the change can still complete them via `completeWithdrawal`, but no new redemptions can enter the queue. This constitutes a **temporary freezing of funds** for all current rsETH holders who have not yet initiated a withdrawal.

---

### Likelihood Explanation

The LRT admin (`DEFAULT_ADMIN_ROLE` in `LRTConfig`) may set this value to an extreme number as an ad-hoc emergency measure — for example, to halt new withdrawal initiations while allowing existing queued withdrawals to drain — without realising the action creates an implicit, undocumented lock. The protocol already has an explicit `pause()` mechanism; the absence of an upper bound on `minRsEthAmountToWithdraw` means a second, implicit lock path exists with no on-chain indication that a lock is active. Likelihood is low but non-zero given the lack of any guard.

---

### Recommendation

1. Add an upper-bound check in `setMinRsEthAmountToWithdraw`, analogous to the cap in `setWithdrawalDelayBlocks`:

```solidity
uint256 public constant MAX_MIN_RSETH_TO_WITHDRAW = 1_000 ether; // example cap

function setMinRsEthAmountToWithdraw(address asset, uint256 minRsEthAmountToWithdraw_) external onlyLRTAdmin {
    if (minRsEthAmountToWithdraw_ > MAX_MIN_RSETH_TO_WITHDRAW) revert MinWithdrawTooHigh();
    minRsEthAmountToWithdraw[asset] = minRsEthAmountToWithdraw_;
    emit MinAmountToWithdrawUpdated(asset, minRsEthAmountToWithdraw_);
}
```

2. If a per-asset withdrawal initiation freeze is a desired emergency capability, implement it as an explicit boolean flag (e.g., `isWithdrawalInitiationEnabled[asset]`) with a dedicated event, so the lock is transparent on-chain and in monitoring tooling.

---

### Proof of Concept

1. LRT admin calls `setMinRsEthAmountToWithdraw(stETH, type(uint256).max)`.
2. User holding 10 rsETH calls `initiateWithdrawal(stETH, 10e18, "")`.
3. The check at line 162 evaluates `10e18 < type(uint256).max` → `true` → reverts with `InvalidAmountToWithdraw`.
4. The same revert occurs for `instantWithdrawal` (line 224).
5. No user can queue a new stETH withdrawal until the admin calls `setMinRsEthAmountToWithdraw(stETH, reasonableValue)` again.
6. The contract emits no "locked" event; external observers see only the `MinAmountToWithdrawUpdated` event with an opaque large number. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L162-164)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L224-226)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L330-333)
```text
    function setMinRsEthAmountToWithdraw(address asset, uint256 minRsEthAmountToWithdraw_) external onlyLRTAdmin {
        minRsEthAmountToWithdraw[asset] = minRsEthAmountToWithdraw_;
        emit MinAmountToWithdrawUpdated(asset, minRsEthAmountToWithdraw_);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L338-343)
```text
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

        withdrawalDelayBlocks = withdrawalDelayBlocks_;
        emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
```
