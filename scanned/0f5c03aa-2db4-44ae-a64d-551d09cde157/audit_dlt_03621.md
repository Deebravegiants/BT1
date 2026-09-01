# [M] [ADRIRO-NEW-M-05] Rewarder should not be allowed to apply rewards on CVX tokens

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-10-asymmetry-mitigation
Published: 2023-10-25
Source: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/58
Type: code-finding

## Details
# Lines of code

https://github.com/asymmetryfinance/afeth/blob/74f340568480aa03d043e970fcf2578bea037cf6/contracts/strategies/votium/VotiumStrategyCore.sol#L301


# Vulnerability details

## Summary

The rewarder role should not be allowed to modify the balance of CVX tokens when applying rewards, otherwise the internal CVX balance tracking could get out of sync with major consequences for the protocol.

## Impact

The introduction of internal CVX balance tracking in the VotiumStrategy contract requires utmost care when handling token movements. Accounting should be done properly, as this essentially tracks the balance of CVX tokens that belong to depositors.

One of these sensitive areas is the `applyRewards()` function. This function is used by the rewarder role to swap arbitrary tokens from claimed rewards into ETH, in order to be compounded back into the protocol.

The current implementation of `applyRewards()` is extremely opaque. While the documentation says that the rewarder role will use the 0x protocol to process the swaps, the function executes arbitrary approvals and calls in its implementation, as can be seen in lines 320-323 and 325-327:

```solidity
301:     function applyRewards(
302:         SwapData[] calldata _swapsData,
303:         uint256 _safEthMinout,
304:         uint256 _cvxMinout
305:     ) public onlyRewarder {
306:         uint256 ethBalanceBefore = address(this).balance;
307:         for (uint256 i = 0; i < _swapsData.length; i++) {
308:             // Some tokens do not allow approval if allowance already exists
309:             uint256 allowance = IERC20(_swapsData[i].sellToken).allowance(
310:                 address(this),
311:                 address(_swapsData[i].spender)
312:             );
313:             if (allowance != type(uint256).max) {
314:                 if (allowance > 0) {
315:                     IERC20(_swapsData[i].sellToken).safeApprove(
316:                         address(_swapsData[i].spender),
317:                         0
318:                     );
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-10-asymmetry-mitigation-findings/issues/58_
