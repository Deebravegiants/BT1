# [H] 6.5 Flawed Fee and Premium Structure

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Specification Changed

When swapping, a fee is charged and borrows pay a premium on their position. Both amounts end up in
the pool without separate accounting. This has various implication. All arising from the fact that the
underlying calculation are based on the pool's reserve, which includes the fees and premiums. All
operations that pay out a proportion of the reserve amounts - also pay out parts of the fees and
premiums. Hence, each time remove, repay, swap or borrow is called, fees and premiums are payed
out. Regardless of the callee is entitled to receive these fees.

The most severe issue is the swap function. Swapping on the pool's reserve, which includes the
collected fees, will nullify all previous fees and prevent fee accumulation. Hence, liquidity providers will
not earn fees collected during the lifetime of the pool, but only the fee from the last swap.

Other examples for issues are shared (even with non-eligible users) premiums and fees, participating on
fees and premiums repeatedly. E.g. a liquidity provider that does not take the risk of lending their token
gets a share of the premium. A borrower gets part of the premium and fees of others. All this can be
leveraged through repeating the operation.

```
Version 2 Specification changed
```
This version of the code introduces a novel fee structure.

```
Version 3 Specification changed
```
The respective code has been updated according to the new specifications of Version 3 which assume
fees only during swaps.
