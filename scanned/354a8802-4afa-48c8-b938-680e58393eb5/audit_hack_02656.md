# [M] Credited amount can be calculated wrong. QueueInternal._swapForPoolTokens doesn't check the token balance and relies on Exchange contract

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L217-L253
Type: audit-issue

## Details
# Credited amount can be calculated wrong. QueueInternal._swapForPoolTokens doesn't check the token balance and relies on Exchange contract

## Summary
QueueInternal._swapForPoolTokens [function](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L217-L253) uses `Exchange` to swap tokens provided by user to `ERC20` [token](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L36) that the queue holds. The amount that was swapped to `ERC20` is taken from `Exchange` return [result](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L236).

However, this is not the best option to check the amount received here as there can be some tokens that behave unusual(like fee on transfer tokens) or `Exchange` contract could be somehow compromised and will return wrong results. I believe that you should just check the `ERC20` balance of queue before swap and after. That will be the correct amount all the time.


Also the same approach is used in `AuctionInternal._swapForPoolTokens`[function](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L605-L641).

## Vulnerability Detail
Described above

## Impact
Credited amount can be calculated wrong.

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L236-L245
## Tool used

Manual Review

## Recommendation
Check `ERC20` balance of `Queue` before and after the swap and use the difference as deposit.
