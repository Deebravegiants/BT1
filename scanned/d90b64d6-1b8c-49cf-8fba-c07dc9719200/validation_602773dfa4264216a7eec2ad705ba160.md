### Title
Pending rsETH Locked in `LRTWithdrawalManager` Cannot Be Recovered During Protocol Pause - (File: contracts/LRTWithdrawalManager.sol)

### Summary
When a user calls `initiateWithdrawal()`, their rsETH is immediately transferred into `LRTWithdrawalManager`. If the protocol is subsequently paused — either automatically by the oracle's price-drop circuit-breaker or manually via `pauseAll()` — there is no mechanism for users to cancel their pending requests and reclaim their locked rsETH. Every user-facing exit path is gated by `whenNotPaused`.

### Finding Description

`initiateWithdrawal()` pulls rsETH from the caller into the contract at line 166:

```solidity
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

The rsETH is not burned at this point. It sits in the contract until an operator calls `unlockQueue()`, which burns it at line 305:

```solidity
if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
```

Every function that could return value to the user or advance the queue is blocked by `whenNotPaused`:

| Function | Modifier |
|---|---|
| `initiateWithdrawal()` | `whenNotPaused` (line 158) |
| `completeWithdrawal()` | `whenNotPaused` (line 183) |
| `completeWithdrawalForUser()` | `whenNotPaused` (line 199) |
| `instantWithdrawal()` | `whenNotPaused` (line 219) |
| `unlockQueue()` | `whenNotPaused` (line 279) |

There is no `cancelWithdrawal()` function, no emergency rsETH-return path, and no admin rescue function for the rsETH held in pending requests. The only admin sweep function, `sweepRemainingAssets()`, transfers LST/ETH balances to the treasury — not rsETH back to users.

The pause can be triggered without any admin action: `LRTOracle.updateRSETHPrice()` automatically pauses `LRTWithdrawalManager` when the rsETH price drops beyond `pricePercentageLimit`.

### Impact Explanation

Users who have called `initiateWithdrawal()` before a pause have their rsETH locked in `LRTWithdrawalManager` with no recovery path. If the pause is temporary, this is a temporary freeze of funds. If the pause is indefinite (e.g., a critical exploit is discovered and the protocol is wound down), the rsETH is permanently frozen in the contract. The rsETH has real market value and represents the user's restaked position.

**Impact: Temporary (potentially permanent) freezing of user rsETH funds.**

### Likelihood Explanation

The pause trigger is partially automated. `LRTOracle.updateRSETHPrice()` calls `withdrawalManager.pause()` whenever the new rsETH price falls more than `pricePercentageLimit` below the all-time high. This is a realistic scenario during any significant slashing event or market dislocation — exactly the conditions under which users would want to withdraw. Additionally, any address holding `PAUSER_ROLE` can call `pauseAll()` at any time.

**Likelihood: Medium** — the automatic oracle-triggered pause makes this a realistic scenario, not a theoretical one.

### Recommendation

Add a `cancelWithdrawal()` function (callable even while paused, i.e., decorated with `whenPaused` or no pause guard) that allows a user to cancel their oldest pending-but-not-yet-unlocked withdrawal request and receive their rsETH back. Alternatively, add an admin-callable emergency function to return rsETH to users with pending requests during a pause.

### Proof of Concept

1. User calls `initiateWithdrawal(stETH, 10e18, "")`. rsETH is transferred to `LRTWithdrawalManager`. [1](#0-0) 

2. Before `unlockQueue()` is called, the rsETH price drops sharply. `LRTOracle.updateRSETHPrice()` detects the drop and calls `withdrawalManager.pause()`. [2](#0-1) 

3. User attempts `completeWithdrawal(stETH, "")` — reverts: `whenNotPaused`. [3](#0-2) 

4. User attempts `instantWithdrawal(stETH, ...)` — reverts: `whenNotPaused`. [4](#0-3) 

5. Operator attempts `unlockQueue(stETH, ...)` — reverts: `whenNotPaused`. [5](#0-4) 

6. No `cancelWithdrawal()` or rsETH-rescue function exists anywhere in the contract. The user's rsETH remains locked in `LRTWithdrawalManager` for the duration of the pause with no recovery path. [6](#0-5)

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

**File:** contracts/LRTWithdrawalManager.sol (L183-184)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
```

**File:** contracts/LRTWithdrawalManager.sol (L219-219)
```text
        whenNotPaused
```

**File:** contracts/LRTWithdrawalManager.sol (L279-279)
```text
        whenNotPaused
```

**File:** contracts/LRTOracle.sol (L277-280)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
```
