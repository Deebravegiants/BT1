# [M] `StargateStrategy#_withdraw`: ether becomes trapped in the contract whenever a user withdraws

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1519
Type: code-finding

## Details
# Lines of code

 https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/stargate/StargateStrategy.sol#L259


# Vulnerability details

## Impact

Upon withdrawing funds from `StargateStrategy`, due to an incorrect assumption in `_withdraw`, the full amount is not refunded but instead remains in the contract as native ETH, resulting in a loss of funds for the withdrawing user.

## Proof of Concept

We will assume here that `amount > queued` and the code inside the `if` statement is executed.

In `_withdraw`, the amount of LP tokens to withdraw is stored as `toWithdraw`, and withdrawn by calling `lpStaking.withdraw` (L252). Then, the Stargate Router is used to redeem these LP tokens and receive native ETH (L253-L257). The ether is wrapped (L259) and sent to the `to` address specified as a parameter (L266).

The problem is that the code assumes that the amount of ETH received after calling `router.instantRedeemLocal` is equal to the amount of LP tokens redeemed (`toWithdraw`), which is not necessarily the case (and indeed not likely). Since only `toWithdraw` amount of ETH is wrapped, the remainder is left in the contract after the transaction completes, resulting in a loss of funds for the user.

```solidity
File: tapioca-yieldbox-strategies-audit\contracts\stargate\StargateStrategy.sol

241:     function _withdraw(
242:         address to,
243:         uint256 amount
244:     ) internal override nonReentrant {
245:         uint256 available = _currentBalance();
246:         require(available >= amount, "StargateStrategy: amount not valid");
247: 
248:         uint256 queued = wrappedNative.balanceOf(address(this));
249:         if (amount > queued) {
250:             compound("");
251:             uint256 toWithdraw = amount - queued;
252:             lpStaking.withdraw(lpStakingPid, toWithdraw);
253:             router.instantRedeemLocal(
254:                 uint16(lpRouterPid),
255:                 toWithdraw,
256:                 address(this)
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1519_
