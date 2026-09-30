# [M] 6.8 Users Can Avoid Paying Fees On Closure

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

On account closure, all the assets held by the account are converted to the underlying token through
defaultSwapContract which is set to be UniswapV2. For this conversion, the user defines a path of
tokens to the underlying. This path can contain arbitrary tokens, tokens even controlled by the user. A
check in _closeCreditAccountImpl assures that the closure of a credit account will not lead to
losses for the protocol i.e., require(loss <= 1). On the closure of an account users are supposed to
return to pool the amount they borrowed, the interest accrued for that amount and an extra amount for
fees namely, feeSuccess and feeInterest. It is important to note that if the funds do not suffice
totalFunds < amountToPool then only the borrowed amount with the interest accrued is returned
and no fees are required to be paid. This means that draining a credit account to the point that does not
make losses can allow a user to avoid paying fees to the protocol.


Code Corrected:

A new check has been introduced which requires that remainingFunds > 0. This way it is guaranteed
that the user has paid their fees. Due to this requirement, a closure that does not result in fee payout will
be reverted. Hence, the only option for the users will be to repay.
