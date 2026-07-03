### Title
Instant Withdrawal Fee Applied at Execution Time With No Slippage Guard Allows Manager to Extract More Than Expected From Users - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`setInstantWithdrawalFee` takes effect immediately with no timelock, and `instantWithdrawal` applies the live fee at execution time with no minimum-output parameter. A user who submits `instantWithdrawal` when the fee is low (or zero) can have their rsETH burned and receive up to 10% less than they observed, with no on-chain recourse. The protocol's own NatSpec acknowledges this: *"Managers can raise it right before this call, making withdrawals cost more than expected."*

### Finding Description
`setInstantWithdrawalFee` is callable by any address holding the `MANAGER` role and takes effect in the same block with no delay:

```solidity
// LRTWithdrawalManager.sol L372-376
function setInstantWithdrawalFee(uint256 feeBasisPoints) external onlyLRTManager {
    if (feeBasisPoints > 1000) revert FeeTooHigh(); // Max 10%
    instantWithdrawalFee = feeBasisPoints;
    emit InstantWithdrawalFeeUpdated(feeBasisPoints);
}
```

`instantWithdrawal` reads `instantWithdrawalFee` at execution time. Critically, rsETH is burned **before** the fee is deducted, and there is no `minAmountOut` parameter:

```solidity
// LRTWithdrawalManager.sol L228-250
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked); // rsETH gone
...
uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
uint256 userAmount = assetAmountUnlocked - fee;
...
_transferAsset(asset, msg.sender, userAmount);
```

The NatSpec on `instantWithdrawal` explicitly documents the exposure:

```
/// @dev Uses the fee set at execution time. Managers can raise it right before this call,
/// making withdrawals cost more than expected.
```

There is no two-step commit/reveal, no timelock, and no user-supplied slippage bound to protect against a fee change landing between the user's off-chain observation and on-chain execution.

### Impact Explanation
A user who observes `instantWithdrawalFee = 0` and submits `instantWithdrawal` for, say, 10 ETH worth of rsETH can have the fee raised to 1000 bps (10%) before their transaction is included. Their rsETH is irrevocably burned and they receive 9 ETH instead of 10 ETH. The 1 ETH difference is transferred to `instantWithdrawalFeeRecipient`. This constitutes a direct, irreversible loss of user funds with no on-chain protection available to the user.

**Impact: High — Theft of unclaimed yield / user withdrawal proceeds.**

### Likelihood Explanation
The `MANAGER` role is a hot-wallet operational key used for routine protocol management. A fee change requires a single transaction from one key. The scenario does not require key compromise — it can occur through accidental timing (a legitimate fee update landing in the same block as a user withdrawal) or through deliberate ordering. The code's own NatSpec treats this as a known, unmitigated condition, confirming the path is realistic.

### Recommendation
1. Add a `minAmountOut` parameter to `instantWithdrawal` so users can specify the minimum asset amount they accept. Revert if `userAmount < minAmountOut`.
2. Introduce a timelock (e.g., two-step commit with a mandatory delay) on `setInstantWithdrawalFee`, consistent with the pattern already used for `TIMELOCK_ROLE`-gated functions elsewhere in the pool contracts.

### Proof of Concept
1. `instantWithdrawalFee` is 0; user calls `instantWithdrawal(ETH, 10 ether rsETH, "")`.
2. Manager calls `setInstantWithdrawalFee(1000)` in the same block with higher gas, landing first.
3. User's transaction executes: rsETH is burned at line 229; fee computed as `10 ether * 1000 / 10_000 = 1 ether`; user receives 9 ether.
4. User has lost 1 ETH with no recourse — the burn is irreversible and there was no slippage guard to abort the call.

---

**Root cause:** [1](#0-0) 

**Acknowledged in NatSpec:** [2](#0-1) 

**rsETH burned before fee applied (no undo):** [3](#0-2) 

**No `minAmountOut` in function signature:** [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L210-211)
```text
    /// @dev Uses the fee set at execution time. Managers can raise it right before this call, making withdrawals cost
    /// more than expected.
```

**File:** contracts/LRTWithdrawalManager.sol (L212-216)
```text
    function instantWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
```

**File:** contracts/LRTWithdrawalManager.sol (L228-238)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);

        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;
```

**File:** contracts/LRTWithdrawalManager.sol (L372-376)
```text
    function setInstantWithdrawalFee(uint256 feeBasisPoints) external onlyLRTManager {
        if (feeBasisPoints > 1000) revert FeeTooHigh(); // Max 10%
        instantWithdrawalFee = feeBasisPoints;
        emit InstantWithdrawalFeeUpdated(feeBasisPoints);
    }
```
