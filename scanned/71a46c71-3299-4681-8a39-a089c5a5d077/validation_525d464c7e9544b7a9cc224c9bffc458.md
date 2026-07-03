### Title
ETH Deposit Limit Check Ignores Deposit Amount, Allowing Limit Bypass - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` applies a fundamentally different (and broken) check for ETH versus ERC20 assets. For ETH, the incoming `amount` is silently ignored, so the limit is never enforced against the new deposit. Any unprivileged depositor can push the protocol's ETH holdings arbitrarily above the configured cap in a single call.

### Finding Description
The function `_checkIfDepositAmountExceedesCurrentLimit` has two branches:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
```

For every ERC20 asset the check is `totalAssetDeposits + amount > limit`, which correctly prevents a deposit that would push the running total over the cap. For ETH the check is only `totalAssetDeposits > limit`, which tests whether the total **already** exceeds the limit before the deposit lands. The `amount` argument is never used.

Consequence: as long as the current ETH total has not yet crossed the limit, any deposit of any size is accepted — including one that is orders of magnitude larger than the remaining headroom. [1](#0-0) 

The caller path is `depositETH` → `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit`. [2](#0-1) [3](#0-2) 

### Impact Explanation
The ETH deposit limit (`depositLimitByAsset`) is the protocol's primary risk-management cap on ETH exposure. Bypassing it allows the protocol to accumulate far more ETH than the limit intends, which can:

- Push ETH restaked in EigenLayer beyond the protocol's intended capacity, potentially causing withdrawal queues to back up and temporarily freezing user funds.
- Violate the invariant that `getTotalAssetDeposits(ETH) ≤ depositLimitByAsset(ETH)`, breaking any off-chain or on-chain logic that relies on this bound.

**Impact: Low — Contract fails to deliver promised returns (deposit cap is not enforced for ETH).**

### Likelihood Explanation
The entry point is the public, permissionless `depositETH` function. No special role, flash loan, or price manipulation is required. Any depositor who sends ETH while the current total is below the limit can exceed the cap in a single transaction. Likelihood is **High**.

### Recommendation
Apply the same `amount`-inclusive check for ETH that is already used for ERC20 assets:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This unifies the logic and correctly prevents any single deposit — ETH or ERC20 — from pushing the running total above the configured limit.

### Proof of Concept
Assume `depositLimitByAsset(ETH) = 1000 ether` and `getTotalAssetDeposits(ETH) = 999 ether`.

1. Attacker calls `depositETH{value: 10_000 ether}(0, "")`.
2. `_checkIfDepositAmountExceedesCurrentLimit(ETH, 10_000 ether)` evaluates `999 ether > 1000 ether` → `false`.
3. The function returns `false` (not exceeded), so `_beforeDeposit` does not revert.
4. `_mintRsETH` mints rsETH for the full 10,000 ETH.
5. `getTotalAssetDeposits(ETH)` is now 10,999 ETH — 10× the intended cap — with no revert at any step. [1](#0-0)

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
```
