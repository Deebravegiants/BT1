Audit Report

## Title
Silent Zero-Return in `_withdrawFromAave` When `totalETHDepositedToAave == 0` Blocks User Withdrawals — (`contracts/LRTWithdrawalManager.sol`)

## Summary
When all principal has been withdrawn from Aave and `totalETHDepositedToAave` reaches `0`, but accrued interest leaves `aaveAWETH.balanceOf(address(this)) > 0`, `_withdrawFromAave` silently returns `0` without reverting. Any subsequent `completeWithdrawal()` call that requires ETH from Aave will then revert with `InsufficientLiquidityForWithdrawal`, blocking affected users until new principal ETH enters the contract. The accrued interest is only recoverable via `collectInterestToTreasury()`, which routes it to the treasury rather than satisfying pending user withdrawals.

## Finding Description
In `_withdrawFromAave` (L905–921), the function deliberately caps withdrawable amount to `totalETHDepositedToAave` (the tracked principal):

```solidity
// L912–915
uint256 withdrawablePrincipal = aaveBalance < totalETHDepositedToAave
    ? aaveBalance
    : totalETHDepositedToAave;   // = 0 when principal fully withdrawn

withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;
if (withdrawnAmount == 0) return 0;  // silent return
```

The guard at L909 (`if (aaveBalance == 0) revert InsufficientAaveBalance()`) does not fire because `aaveBalance > 0` (interest remains). The function returns `0` silently with no revert, no event, and no ETH moved.

The caller `_processWithdrawalCompletion` (L720–730) then checks the post-call balance:

```solidity
_withdrawFromAave(amountNeeded);   // returns 0 silently
uint256 balanceAfter = address(this).balance;
if (balanceAfter < request.expectedAssetAmount) {
    revert InsufficientLiquidityForWithdrawal();  // always fires
}
```

**Reachable state sequence:**
1. ETH deposited to Aave: `totalETHDepositedToAave = P`, `aaveBalance = P`.
2. Interest accrues: `aaveBalance = P + I`.
3. Users call `completeWithdrawal()` repeatedly; each call decrements `totalETHDepositedToAave` by the withdrawn amount.
4. After sufficient completions: `totalETHDepositedToAave = 0`, `aaveBalance = I > 0`.
5. Any subsequent `completeWithdrawal()` that needs ETH from Aave silently gets `0` and reverts.

`_collectInterestToTreasury()` (L950–952) correctly handles this state — when `principal == 0`, `aaveBalance > principal` passes, and the full `aaveBalance` is sent to treasury — but this does not unblock user withdrawals; it only drains the interest away from the contract.

## Impact Explanation
**Medium. Temporary freezing of funds.**

Users with unlocked, pending withdrawal requests for ETH are blocked from completing their withdrawals. The freeze persists until new principal ETH is deposited into the contract (either directly or via Aave). The accrued interest that could theoretically cover the shortfall is inaccessible for user withdrawals by design and is routed to treasury instead. No user funds are permanently lost, but withdrawals are blocked pending external action.

## Likelihood Explanation
No privileged role, oracle manipulation, or attacker action is required. Interest accrues automatically in Aave over time. Users calling `completeWithdrawal()` is the normal, intended flow. The longer ETH sits in Aave and the more withdrawals are processed, the more likely `totalETHDepositedToAave` reaches `0` while `aaveBalance > 0`. This is a normal operational state reachable through entirely permissionless actions.

## Recommendation
In `_withdrawFromAave`, when `totalETHDepositedToAave == 0` but `aaveBalance > 0`, the function should revert with a descriptive error (e.g., `OnlyInterestRemains`) rather than silently returning `0`. This allows `_processWithdrawalCompletion` to handle the case explicitly — for example, by calling `_collectInterestToTreasury()` first to clear the interest balance, then re-evaluating whether the contract's ETH balance is sufficient, or by allowing interest to fund user withdrawals up to `aaveBalance` when `totalETHDepositedToAave == 0`.

## Proof of Concept
```solidity
// State: totalETHDepositedToAave = 0, aaveAWETH.balanceOf(withdrawalManager) = 1e18 (pure interest)
// address(this).balance = 0

// User calls completeWithdrawal() for 1e18 ETH:
// 1. contractBalance (0) < request.expectedAssetAmount (1e18) → enters Aave branch
// 2. amountNeeded = 1e18
// 3. _withdrawFromAave(1e18):
//    - amount != 0 → continues
//    - aaveBalance = 1e18 != 0 → no InsufficientAaveBalance revert
//    - withdrawablePrincipal = min(1e18, 0) = 0
//    - withdrawnAmount = min(1e18, 0) = 0
//    - withdrawnAmount == 0 → return 0 (silent, no ETH moved)
// 4. balanceAfter = 0 < 1e18 → revert InsufficientLiquidityForWithdrawal
// 5. User withdrawal is blocked; 1e18 aWETH remains in Aave
// 6. collectInterestToTreasury() sends 1e18 to treasury, not to user
``` [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L720-731)
```text
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
```

**File:** contracts/LRTWithdrawalManager.sol (L905-921)
```text
    function _withdrawFromAave(uint256 amount) internal returns (uint256 withdrawnAmount) {
        if (amount == 0) return 0;

        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        if (aaveBalance == 0) revert InsufficientAaveBalance();

        // Only withdraw up to the principal amount (don't use accrued interest for user withdrawals)
        uint256 withdrawablePrincipal = aaveBalance < totalETHDepositedToAave ? aaveBalance : totalETHDepositedToAave;

        withdrawnAmount = amount > withdrawablePrincipal ? withdrawablePrincipal : amount;
        if (withdrawnAmount == 0) return 0;

        aaveWETHGateway.withdrawETH(aavePool, withdrawnAmount, address(this));
        totalETHDepositedToAave -= withdrawnAmount;

        emit ETHWithdrawnFromAave(withdrawnAmount, totalETHDepositedToAave);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L945-958)
```text
    function _collectInterestToTreasury() internal returns (uint256 interestAmount) {
        uint256 aaveBalance = aaveAWETH.balanceOf(address(this));
        uint256 principal = totalETHDepositedToAave;

        // Return 0 if no interest or balance is less than principal (accounting for rounding)
        if (aaveBalance <= principal) return 0;

        interestAmount = aaveBalance - principal;

        aaveWETHGateway.withdrawETH(aavePool, interestAmount, address(this));

        address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        (bool sent,) = payable(treasury).call{ value: interestAmount }("");
        if (!sent) revert TreasuryTransferFailed();
```
