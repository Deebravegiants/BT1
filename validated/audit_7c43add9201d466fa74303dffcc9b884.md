### Title
`instantWithdrawalFee` Applied at Execution Time With No User Slippage Protection — (`File: contracts/LRTWithdrawalManager.sol`)

### Summary

The `instantWithdrawal` function in `LRTWithdrawalManager` applies `instantWithdrawalFee` at the moment of execution, not at the moment the user decides to withdraw. The manager can update this fee at any time via `setInstantWithdrawalFee`. There is no `minAmountOut` or equivalent slippage guard in `instantWithdrawal`, so a user who checks the fee before submitting their transaction may receive materially less than expected if the fee is raised before their transaction is mined. The code itself acknowledges this in a developer comment.

### Finding Description

`instantWithdrawal` is a single-step, publicly callable function that burns the caller's rsETH and immediately transfers the underlying asset minus a fee: [1](#0-0) 

The fee deducted is read from the mutable state variable `instantWithdrawalFee` at the time the transaction executes: [2](#0-1) 

The manager can change this fee at any time, up to a maximum of 10 % (1000 bps), with no time-lock or delay: [3](#0-2) 

The developer comment directly above `instantWithdrawal` explicitly acknowledges the problem: [4](#0-3) 

There is no parameter in `instantWithdrawal` that lets the caller specify the maximum fee they are willing to accept, so the user has no on-chain protection against a fee change that occurs between when they read `instantWithdrawalFee` off-chain and when their transaction is included in a block.

### Impact Explanation

A user who observes `instantWithdrawalFee = 0` (or any low value), submits `instantWithdrawal`, and has the fee raised to 1000 bps (10 %) before their transaction mines will receive 10 % less of the underlying asset than they expected. Their rsETH is burned atomically and cannot be recovered. The contract fails to deliver the return the user anticipated at the time of submission. This maps to the **Low** impact tier: *"Contract fails to deliver promised returns, but doesn't lose value."*

### Likelihood Explanation

The `LRTManager` role is a live operational key used for routine parameter updates. A fee change does not require governance or a time-lock. Any fee update that races with a pending `instantWithdrawal` transaction in the mempool — whether intentional or coincidental — triggers the discrepancy. Because `instantWithdrawal` is the only path for immediate rsETH redemption, users under time pressure (e.g., liquidation risk) cannot avoid it.

### Recommendation

Add a `minAmountOut` (or `maxFeeBps`) parameter to `instantWithdrawal` and revert if the fee-adjusted payout falls below the caller's stated minimum:

```solidity
function instantWithdrawal(
    address asset,
    uint256 rsETHUnstaked,
    uint256 minAmountOut,   // <-- new
    string calldata referralId
) external ... {
    ...
    uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
    uint256 userAmount = assetAmountUnlocked - fee;
    if (userAmount < minAmountOut) revert SlippageExceeded();
    ...
}
```

This mirrors the fix suggested in M-07: lock in the fee parameters known to the user at the time they commit to the action.

### Proof of Concept

1. `instantWithdrawalFee` is currently 0 bps. Alice calls `instantWithdrawal` with 10 rsETH, expecting to receive `X` ETH.
2. Before Alice's transaction is mined, the manager calls `setInstantWithdrawalFee(1000)` (10 %).
3. Alice's transaction mines. Line 237 computes `fee = assetAmountUnlocked * 1000 / 10_000`, deducting 10 % from her payout.
4. Alice receives `0.9 * X` ETH. Her rsETH has already been burned at line 229; there is no recourse. [5](#0-4)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L206-253)
```text
    /// @notice Allows users to instantly withdraw their assets by burning rsETH tokens
    /// @param asset The address of the asset (ETH/LST) to withdraw
    /// @param rsETHUnstaked The amount of rsETH tokens to burn for withdrawal
    /// @param referralId The referral identifier for tracking
    /// @dev Uses the fee set at execution time. Managers can raise it right before this call, making withdrawals cost
    /// more than expected.
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

**File:** contracts/LRTWithdrawalManager.sol (L372-376)
```text
    function setInstantWithdrawalFee(uint256 feeBasisPoints) external onlyLRTManager {
        if (feeBasisPoints > 1000) revert FeeTooHigh(); // Max 10%
        instantWithdrawalFee = feeBasisPoints;
        emit InstantWithdrawalFeeUpdated(feeBasisPoints);
    }
```
