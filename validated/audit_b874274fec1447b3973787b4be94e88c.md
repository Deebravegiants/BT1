### Title
No Cancellation Path for Pending Withdrawal Requests Permanently Locks User rsETH — (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager.initiateWithdrawal()` immediately transfers the user's rsETH into the contract as the first step of the withdrawal flow. No cancellation or refund function exists anywhere in the codebase. If the contract is paused — or if the operator queue-unlock step becomes permanently unavailable — the user's rsETH is locked in the contract with no self-help recovery path.

---

### Finding Description

When a user calls `initiateWithdrawal()`, their rsETH is pulled into `LRTWithdrawalManager` at the very first step:

```solidity
// LRTWithdrawalManager.sol:166
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

The request is then stored in `withdrawalRequests` and `userAssociatedNonces` via `_addUserWithdrawalRequest()`. [1](#0-0) 

The only path to recover value from this locked rsETH is a two-step sequence:

1. An operator (or asset-transfer role) calls `unlockQueue()`, which has both `whenNotPaused` and `onlyAssetTransferOrOperatorRole` guards, and processes requests in strict FIFO order. [2](#0-1) 

2. The user calls `completeWithdrawal()`, which also has `whenNotPaused` and additionally requires the request to have already been unlocked (`usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]` reverts). [3](#0-2) 

A grep across the entire `contracts/` tree for `cancelWithdrawal`, `refundWithdrawal`, or `cancelRequest` returns **zero matches**. No cancellation or emergency-refund function exists. [4](#0-3) 

The `WithdrawalRequest` struct stores only `rsETHUnstaked`, `expectedAssetAmount`, and `withdrawalStartBlock` — there is no `state` field and no `Failed`/`Cancelled` transition. [5](#0-4) 

---

### Impact Explanation

**Impact: Medium — Temporary (potentially permanent) freezing of user rsETH.**

If the contract is paused by the `PAUSER_ROLE` for any reason (security incident, upgrade, etc.), both `unlockQueue` and `completeWithdrawal` are blocked by `whenNotPaused`. The user's rsETH sits in the contract with no user-initiated exit. If the pause is never lifted — or if the protocol is wound down — the freeze becomes permanent. Even in the non-pause case, a user who submitted a request before a long operator outage has no self-help mechanism; they cannot cancel and redeploy their rsETH elsewhere.

---

### Likelihood Explanation

**Likelihood: Medium.**

The `PAUSER_ROLE` is a live, multi-party role used for security responses. Pauses are a normal operational event. Every pause that occurs while withdrawal requests are in the `Created`/locked state triggers this condition for every affected user. The protocol has no time-bounded unpause guarantee, so a prolonged pause directly translates to a prolonged (or permanent) fund freeze with no user recourse.

---

### Recommendation

Add a user-callable `cancelWithdrawal(address asset)` function that:

1. Pops the user's oldest pending nonce from `userAssociatedNonces[asset][msg.sender]`.
2. Verifies the request has **not** yet been unlocked (`nonce >= nextLockedNonce[asset]`).
3. Decrements `assetsCommitted[asset]` by `request.expectedAssetAmount`.
4. Deletes the `withdrawalRequests[requestId]` entry.
5. Transfers `request.rsETHUnstaked` rsETH back to the user.

Optionally, allow cancellation even after the delay has elapsed if the request remains in the locked state (analogous to the external report's recommendation for user self-cancellation after expiry). This eliminates the trust dependency on operator liveness for fund recovery.

---

### Proof of Concept

1. User calls `initiateWithdrawal(stETH, 10e18, "")`. rsETH is transferred to `LRTWithdrawalManager` at line 166. [6](#0-5) 

2. A security incident occurs; `PAUSER_ROLE` calls `pause()`. [7](#0-6) 

3. User attempts `completeWithdrawal(stETH, "")` → reverts on `whenNotPaused`. [3](#0-2) 

4. Operator attempts `unlockQueue(stETH, ...)` → reverts on `whenNotPaused`. [8](#0-7) 

5. No `cancelWithdrawal` function exists. User's 10 rsETH remains locked in the contract indefinitely with zero recovery path.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L1-30)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.27;

import { UtilLib } from "./utils/UtilLib.sol";
import { LRTConstants } from "./utils/LRTConstants.sol";
import { DoubleEndedQueue } from "./utils/DoubleEndedQueue.sol";

import { LRTConfigRoleChecker, ILRTConfig } from "./utils/LRTConfigRoleChecker.sol";
import { IRSETH } from "./interfaces/IRSETH.sol";
import { ILRTOracle } from "./interfaces/ILRTOracle.sol";
import { ILRTWithdrawalManager } from "./interfaces/ILRTWithdrawalManager.sol";
import { ILRTDepositPool } from "./interfaces/ILRTDepositPool.sol";
import { ILRTUnstakingVault } from "./interfaces/ILRTUnstakingVault.sol";
import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import {
    ReentrancyGuardUpgradeable
} from "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import { SafeERC20 } from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import { IWrappedTokenGatewayV3 } from "./interfaces/aave/IWrappedTokenGatewayV3.sol";
import { IAToken } from "./interfaces/aave/IAToken.sol";
import { IPoolDataProvider } from "./interfaces/aave/IPoolDataProvider.sol";

/// @title LRTWithdrawalManager - Withdraw Manager Contract for rsETH => LSTs
/// @notice Handles LST asset withdraws
contract LRTWithdrawalManager is
    ILRTWithdrawalManager,
    LRTConfigRoleChecker,
    PausableUpgradeable,
    ReentrancyGuardUpgradeable
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

**File:** contracts/LRTWithdrawalManager.sol (L347-349)
```text
    function pause() external onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
    }
```

**File:** contracts/interfaces/ILRTWithdrawalManager.sol (L39-43)
```text
    struct WithdrawalRequest {
        uint256 rsETHUnstaked;
        uint256 expectedAssetAmount;
        uint256 withdrawalStartBlock;
    }
```
