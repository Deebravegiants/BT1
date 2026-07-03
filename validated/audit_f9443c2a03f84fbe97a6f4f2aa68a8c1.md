Audit Report

## Title
Missing Minimum Output Amount (Slippage Protection) in L2 Pool `deposit` Functions - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol, contracts/pools/RSETHPoolV2ExternalBridge.sol, contracts/pools/RSETHPoolNoWrapper.sol)

## Summary
All L2 pool `deposit` functions lack a `minRsETHAmountExpected` parameter, providing no on-chain slippage protection for depositors. The minted output is computed entirely from the oracle rate at execution time, meaning any oracle rate update between transaction submission and mining silently reduces the user's received tokens. The L1 `LRTDepositPool` already implements this protection via `_beforeDeposit`, confirming it is a deliberate security feature absent from the L2 contracts.

## Finding Description
In `LRTDepositPool.sol` (L76–87, L99–117, L667–669), both `depositETH` and `depositAsset` accept a `minRSETHAmountExpected` parameter and enforce it in `_beforeDeposit`:
```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```
In contrast, every L2 pool `deposit` function omits this parameter entirely. In `RSETHPoolV3.sol` (L246–265, L271–293), `RSETHPoolNoWrapper.sol` (L231–244, L250–271), `RSETHPoolV2ExternalBridge.sol` (L289–301), and the other pool variants, the minted amount is computed solely from `viewSwapRsETHAmountAndFee`, which reads the live oracle rate via `getRate()` at execution time (RSETHPoolV3.sol L299–308). There is no check comparing the computed output against any user-supplied minimum. The rsETH oracle rate is updated periodically from L1; any such update landing before a user's deposit transaction is mined will reduce the output with no revert.

## Impact Explanation
**Low — Contract fails to deliver promised returns, but does not lose value.** The depositor's ETH or token is accepted by the pool, but the minted `wrsETH`/`rsETH` output is silently reduced relative to what the user observed off-chain. The ETH/token remains in the pool; no funds are stolen or frozen. This matches the allowed impact: "Contract fails to deliver promised returns, but doesn't lose value."

## Likelihood Explanation
Any unprivileged depositor is affected. No attacker is required: the oracle rate is updated as a routine protocol operation. Any rate update that lands in the same block as, or just before, a user's deposit transaction will silently reduce the user's output. This is a structural property of the missing parameter and will occur on any active L2 deployment whenever the oracle rate changes.

## Recommendation
Add a `minRsETHAmountExpected` parameter to all L2 pool `deposit` functions, mirroring the L1 pattern:
```solidity
function deposit(string memory referralId, uint256 minRsETHAmountExpected)
    external payable nonReentrant whenNotPaused limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmountExpected) revert MinimumAmountToReceiveNotMet();
    wrsETH.mint(msg.sender, rsETHAmount);
}
```
Apply the same fix to the token-deposit overload and to all pool variants.

## Proof of Concept
1. Oracle rate is `1.05e18` (1 rsETH = 1.05 ETH).
2. User simulates `deposit{value: 1 ether}("ref")` off-chain; `viewSwapRsETHAmountAndFee(1e18)` returns `≈0.952 wrsETH`.
3. Before the transaction is mined, the oracle rate is updated to `1.10e18` via the L1→L2 rate propagation system.
4. At execution, `viewSwapRsETHAmountAndFee(1e18)` now returns `≈0.909 wrsETH`.
5. The contract mints `0.909 wrsETH` to the user with no revert — approximately 4.5% fewer tokens than expected, with no on-chain protection.

**Foundry fork test plan:** Fork an L2 deployment; call `getRate()` to record the current rate; prank the oracle updater to increase the rate; call `deposit{value: 1 ether}("ref")` from a user address; assert that the minted balance is less than the amount computed at the pre-update rate, and that no revert occurred.