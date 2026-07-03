Audit Report

## Title
Permissionless `updateRSETHPrice()` With No Staleness Guard Allows Delayed Mempool Transaction to Trigger False-Positive Protocol-Wide Pause - (File: contracts/LRTOracle.sol)

## Summary
`updateRSETHPrice()` is callable by any address with no deadline or staleness protection. Because the downside-protection check compares the freshly computed price against `highestRsethPrice` (a persistent all-time-high), a transaction that was submitted when the price was within tolerance but executes after an intervening update has raised `highestRsethPrice` can cross the threshold and pause `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle` — freezing all user deposits and withdrawals until an admin manually unpauses.

## Finding Description
`updateRSETHPrice()` has no access control and no expiry mechanism: [1](#0-0) 

Inside `_updateRsETHPrice()`, the downside-protection block pauses the entire protocol when the freshly computed price falls below `highestRsethPrice` by more than `pricePercentageLimit`: [2](#0-1) 

`highestRsethPrice` is a persistent all-time-high that is ratcheted upward on every successful price update: [3](#0-2) 

**Exploit flow (concrete, `pricePercentageLimit = 1e16` / 1%):**

1. `highestRsethPrice = 1.00e18`. Current computed price = `1.005e18` (within 1%). A keeper submits `updateRSETHPrice()` with low gas; the transaction enters the mempool but does not land.
2. Before the delayed tx lands, the price rises to `1.02e18`. A second `updateRSETHPrice()` executes successfully, setting `highestRsethPrice = 1.02e18`.
3. The price drifts back to `1.005e18` (normal market movement, still within 1% of the original peak).
4. The delayed transaction from step 1 now executes. `_updateRsETHPrice()` computes `newRsETHPrice = 1.005e18`. The check evaluates: `diff = 1.02e18 − 1.005e18 = 0.015e18`; `pricePercentageLimit.mulWad(highestRsethPrice) = 0.01 × 1.02e18 = 0.0102e18`. Since `0.015e18 > 0.0102e18`, `isPriceDecreaseOffLimit = true`.
5. `lrtDepositPool.pause()`, `withdrawalManager.pause()`, and `_pause()` are called — the protocol is frozen.

No adversarial action is required. A legitimate keeper bot submitting with insufficient gas, or ordinary Ethereum mempool congestion, is sufficient to trigger the condition. There is no existing guard (no deadline parameter, no `block.timestamp` check, no snapshot of `highestRsethPrice` at submission time) that prevents a stale transaction from executing the pause path.

## Impact Explanation
When the protocol is paused, all user-facing operations revert: `depositETH` and `depositAsset` in `LRTDepositPool` (both guarded by `whenNotPaused`), and `initiateWithdrawal`, `completeWithdrawal`, and `instantWithdrawal` in `LRTWithdrawalManager` (all guarded by `whenNotPaused`). [4](#0-3) [5](#0-4) 

Funds already in the withdrawal queue are frozen until an admin manually calls `unpause()` on each contract. This is a concrete **temporary freezing of funds** — Medium severity.

## Likelihood Explanation
- `updateRSETHPrice()` is permissionless; any address (including automated keeper bots) can submit it.
- Ethereum mempool congestion routinely delays low-gas transactions by minutes to hours.
- The scenario requires only normal price volatility (a small rise followed by a return to prior levels) combined with a delayed transaction — no adversarial intent is required.
- The condition becomes more likely as `pricePercentageLimit` is set tighter (e.g., 0.5–1%), which is the intended operational configuration for downside protection.
- The pause can be triggered repeatedly after each admin unpause if the root cause is not fixed.

## Recommendation
Add a `deadline` (or `maxTimestamp`) parameter to `updateRSETHPrice()`. If `block.timestamp > deadline`, revert without executing the pause logic:

```solidity
function updateRSETHPrice(uint256 deadline) public whenNotPaused {
    if (block.timestamp > deadline) revert TransactionExpired();
    _updateRsETHPrice();
}
```

Alternatively, accept a `maxHighestRsethPrice` parameter and revert if the on-chain `highestRsethPrice` has moved beyond the caller's expected value since submission, ensuring stale transactions fail cleanly rather than triggering a false-positive pause.

## Proof of Concept
1. Deploy with `pricePercentageLimit = 1e16` (1%).
2. Set initial state: `rsETHPrice = highestRsethPrice = 1.00e18`.
3. Submit `updateRSETHPrice()` with low gas when current computed price = `1.005e18`. Transaction enters mempool but does not land (simulate by not mining it yet in a Foundry test using `vm.pauseGasMetering` / manual tx ordering).
4. Mine a second `updateRSETHPrice()` call when price = `1.02e18`; assert `highestRsethPrice == 1.02e18`.
5. Set underlying asset values so computed price = `1.005e18`.
6. Mine the delayed transaction from step 3.
7. Assert `lrtDepositPool.paused() == true`, `withdrawalManager.paused() == true`, and `lrtOracle.paused() == true`.
8. Confirm that `depositETH`, `initiateWithdrawal`, and `completeWithdrawal` all revert with the paused error. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTOracle.sol (L293-296)
```text
        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }
```

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
