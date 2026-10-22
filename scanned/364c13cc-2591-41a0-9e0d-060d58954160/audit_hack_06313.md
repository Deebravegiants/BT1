# [M] No "slippage" protection for refunds of deposits

## Summary
Severity: Medium
Reporter: minhtrng
Source: https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/DepositManager/Implementations/DepositManagerV1.sol#L171-L181
Type: audit-issue

## Details
# No "slippage" protection for refunds of deposits

## Summary

Frontrunning a refund of a deposit might cause a user to revoke his one time refund right for much less than he expected (in the worst case nothing).

## Vulnerability Detail

The function `DepositManager.refundDeposit` might decrease the refunded amount depending on what is considered available:

```js
uint256 availableFunds = bounty.getTokenBalance(depToken) -
    bounty.getLockedFunds(depToken);

uint256 volume;
if (bounty.volume(_depositId) <= availableFunds) {
    volume = bounty.volume(_depositId);
} else {
    volume = availableFunds;
}

bounty.refundDeposit(_depositId, msg.sender, volume);
```

Assume the following scenario: 3 users deposit 100 tokens each. 100 of these tokens have been claimed while another 100 tokens (from User3) are still locked. That leaves available funds at 100. Now both User1 and User2 want to refund at the same time. The user whose transaction gets processed second, receives nothing and will not be able to attempt a refund again (when User3 funds unlock), as the refund function sets a flag that prevents multiple refunds of the same deposit:

```js
require(!refunded[_depositId], Errors.DEPOSIT_ALREADY_REFUNDED);
...
refunded[_depositId] = true;
```

## Impact

User will get much less refund than he expected or nothing at all and can not attempt a refund again

## Code Snippet

https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/DepositManager/Implementations/DepositManagerV1.sol#L171-L181

## Tool used

Manual Review

## Recommendation

Add a sort of "slippage protection" (as is known from Uniswap Router functions) and revert, if too little has been withdrawn.
