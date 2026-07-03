### Title
`instantWithdrawalFee` Applied at Execution Time Allows Fee to Differ from User's Expected Rate - (File: contracts/LRTWithdrawalManager.sol)

### Summary
The `instantWithdrawal` function in `LRTWithdrawalManager` applies `instantWithdrawalFee` at the moment of execution rather than locking it at any prior point. The manager can update this fee at any time with no timelock, meaning a user who observes a given fee rate before calling `instantWithdrawal` may receive less than expected if the fee changes before their transaction is mined.

### Finding Description
`instantWithdrawal` computes the fee deduction inline at execution time:

```solidity
uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
uint256 userAmount = assetAmountUnlocked - fee;
``` [1](#0-0) 

The `instantWithdrawalFee` state variable is set by `setInstantWithdrawalFee`, which has no timelock and takes effect immediately:

```solidity
function setInstantWithdrawalFee(uint256 feeBasisPoints) external onlyLRTManager {
    if (feeBasisPoints > 1000) revert FeeTooHigh(); // Max 10%
    instantWithdrawalFee = feeBasisPoints;
    ...
}
``` [2](#0-1) 

The protocol's own NatSpec on `instantWithdrawal` explicitly acknowledges this:

> *"Uses the fee set at execution time. Managers can raise it right before this call, making withdrawals cost more than expected."* [3](#0-2) 

Unlike the Sofa Protocol (where the fee is protected by DAO governance and a timelock), `setInstantWithdrawalFee` in LRT-rsETH has no delay mechanism. The manager can raise the fee from 0 to 10% (1000 bps) in a single transaction with no advance notice.

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

A user who reads `instantWithdrawalFee` before submitting their `instantWithdrawal` transaction may receive materially fewer assets than the rate they observed. The fee can increase by up to 10% (1000 bps) in a single manager transaction. The user's rsETH is burned and they receive `assetAmountUnlocked - fee` where `fee` is computed at the new, higher rate. Funds are not permanently frozen, but the user receives less than the return they expected when initiating the call.

### Likelihood Explanation
**Low.** Exploitation requires either (a) a manager legitimately updating the fee concurrently with a user's pending transaction, or (b) a manager deliberately front-running a user's `instantWithdrawal` call. The `onlyLRTManager` role is trusted, but the absence of any timelock means no on-chain delay separates a fee change from its effect on in-flight user transactions.

### Recommendation
Add a `maxFeeBps` parameter to `instantWithdrawal` that the caller specifies, and revert if `instantWithdrawalFee > maxFeeBps` at execution time. Alternatively, apply a timelock to `setInstantWithdrawalFee` so users have advance notice of fee changes before they take effect.

### Proof of Concept
1. `instantWithdrawalFee` is currently 0 bps. User Alice observes this and submits `instantWithdrawal(ETH, 1e18, "")`.
2. Before Alice's transaction is mined, the manager calls `setInstantWithdrawalFee(1000)` (10%).
3. Alice's transaction executes: `fee = (assetAmountUnlocked * 1000) / 10_000` — Alice receives 10% less than she expected when she submitted the transaction.
4. The fee flows to `instantWithdrawalFeeRecipient` (or the protocol treasury). [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L210-211)
```text
    /// @dev Uses the fee set at execution time. Managers can raise it right before this call, making withdrawals cost
    /// more than expected.
```

**File:** contracts/LRTWithdrawalManager.sol (L237-238)
```text
        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;
```

**File:** contracts/LRTWithdrawalManager.sol (L240-248)
```text
        address feeRecipient = instantWithdrawalFeeRecipient;
        if (feeRecipient == address(0)) {
            // Backwards-compatible default: send fees to the protocol treasury
            feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        }
        if (fee > 0) {
            _transferAsset(asset, feeRecipient, fee);
            emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L372-376)
```text
    function setInstantWithdrawalFee(uint256 feeBasisPoints) external onlyLRTManager {
        if (feeBasisPoints > 1000) revert FeeTooHigh(); // Max 10%
        instantWithdrawalFee = feeBasisPoints;
        emit InstantWithdrawalFeeUpdated(feeBasisPoints);
    }
```
