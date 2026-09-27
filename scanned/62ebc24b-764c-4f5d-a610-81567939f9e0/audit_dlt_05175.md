# [?] Fix overflow bug that occasionally occurs when supplying 0 base (#455)

## Summary
Severity: Unknown
Chain: Compound
Component: compound-finance/comet
Published: 2022-07-01
Source: https://github.com/compound-finance/comet/commit/bf20ccfa991578de670fcb5d6f3ae2362ebc6aa0
Type: security-commit

## Details
Fix overflow bug that occasionally occurs when supplying 0 base (#455)

This PR fixes a math overflow bug that occasionally occurs when supplying 0 base. I also added a unit test to verify the fix, as well as another unit test to show a weird quirk that can occur when withdrawing 0 base. 

**Bug details:**
In `supplyBase`, we calculate `dstPrincipalNew` using `dstPrincipal` (old principal value before amount is supplied). The formula is:

`int104 dstPrincipalNew = principalValue(presentValue(dstPrincipal) + signed104(amount))`

When `amount=0`, the formula condenses to:

`dstPrincipalNew = principalValue(presentValue(dstPrincipal))`

Due to the fact that both `principalValue` and `presentValue` round down in favor of the protocol, we can actually end up with a value of `dstPrincipalNew < dstPrincipal`. 

This breaks our assumption in `repayAndSupplyAmount` that `newPrincipal >= oldPrincipal` MUST be true. In the old code, this would cause `supplyAmount` returned from `repayAndSupplyAmount` to be an extremely large number (`uint104(-1)` to be precise), which would later cause an overflow during an addition operation. The new code now explicitly checks this assumption and sets both `repayAmount` and `supplyAmount` to 0 if the assumption is violated. We apply a similar check in `withdrawAndBorrowAmount` as well.
