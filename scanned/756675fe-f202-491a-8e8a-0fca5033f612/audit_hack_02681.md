# [H] Multiple withdrawals in the same epoch from Auction

## Summary
Severity: High
Reporter: 0xc0ffEE
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L221
Type: audit-issue

## Details
# Multiple withdrawals in the same epoch from Auction

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L221

From EnumerableSet implementation, the function `EnumerableSet.remove` returns a `bool` value that is `true` when `value` is in the set and successfully removed, `false` when the `value` is not in the set.

`l.epochsByBuyer[msg.sender].remove(epoch)` does not check for returned value so the function `_withdraw(AuctionStorage.Layout, uint64)` will still work for the same input params
=> user could withdraw multiple times in the same epoch to drain funds
