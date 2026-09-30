# [H] Repaying GHO on behalf of another user records interest as paid for the sender, not the bor-

## Summary
Severity: High
Contest weight: 0.4050
Dataset id: 14273
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a GHO loan is repaid, it is done through a call to Pool.repay(), the last parameter of which dictates which account
the repayment is to be made for. This in turn calls BorrowLogic.executeRepay() which, on line [255], makes the call:
IAToken(reserveCache.aTokenAddress).handleRepayment(msg.sender, paybackAmount);
This will be a call to
GhoAToken.handleRepayment() but, critically, the parameters contain only the address of the
payment sender. The borrower’s address, params.onBehalfOf, is not sent to GhoAToken.handleRepayment() at all.
Within GhoAToken.handleRepayment(), the interest owed is assessed on line [170]:
uint256 balanceFromInterest = _ghoVariableDebtToken.getBalanceFromInterest(user);
However, in this context, the value of user will be msg.sender, and so the interest value used will be that of the
sender, not the borrower. The interest payment will also be credited to the sender, not the borrower because user is
used to determine which account to credit on line [284]:
_ghoVariableDebtToken.decreaseBalanceFromInterest(user, amount);
Note that any GHO spent is still all burned from the sender and any GhoVariableDebtToken burned are still always burned
from the borrower. The main impact of this issue is in the accounting and in terms of where the interest is paid to.
Consider a complete repayment of a GHO debt on behalf of another account in the two following scenarios:
1. The sender has zero GHO debt
balanceFromInterest in
GhoAToken.handleRepayment() will be zero, and so the full amount of the debt will
be burnt on line [175]. The treasury will receive zero GHO when it should have received interest. Moreover,
the value of
GhoVariableDebtToken._ghoUserState[user].accumulatedDebtInterest will remain at the value
of the interest owed by the borrower, even though that account would have no GHO, no
GhoAToken and no
GhoVariableDebtToken.
The main impact of this issue is the lost interest to the treasury in this case.
There is also an accounting error in
GhoVariableDebtToken._ghoUserState[user].accumulatedDebtInterest.
If
the
borrower
borrows
GHO
in
future,
repayments
will
send
this
extra
amount
to
the
treasury,
but
without
affecting
the
amount
repaid.
This
has
the
effect
of
balancing
the
books
by
effectively
paying
the
originally
unpaid
interest.
However,
the
other
effect
of
this
accounting
error
is
that
calls
to
GhoVariableDebtToken.getBalanceFromInterest()
will
have
unexpectedly
high
values,
and
this
might
cause
security
in future.
2. The sender has a large GHO debt with a large owed interest amount
GHO Stablecoin
This scenario is more complex, but resolves very similarly to the first. The repaid amount is initially credited
entirely to the sender’s GhoVariableDebtToken._ghoUserState[user].accumulatedDebtInterest.
The borrower’s value of
GhoVariableDebtToken._ghoUserState[user].accumulatedDebtInterest remains un-
changed and the borrower can withdraw their collateral. The borrower’s account behaves identically to the first
scenario.
The sender’s account, despite having interest credited in the variable:
GhoVariableDebtToken._ghoUserState[user].accumulatedDebtInterest
still has the same balance of GhoVariableDebtToken as if it had not made any repayments, so this interest "credit"
is illusory. The account will still need to repay its full amount of GHO and the amount that the treasury receives is
the total amount owed by the sender.
The borrower’s interest, in this scenario, is lost in the same way as in the first.
There are multiple accounting errors in GhoVariableDebtToken._ghoUserState[user].accumulatedDebtInterest
throughout this scenario for both borrower and sender.

## Recommendation
Consider modifying
BorrowLogic.executeRepay() so that its calls to
GhoAToken.handleRepayment() also pass on
the value of
params.onBehalfOf.
This may be a desirable measure generally, given the stated purpose of
GhoAToken.handleRepayment():
* @dev The default implementation is empty as with standard ERC20 tokens, nothing needs to be done after the
* transfer is concluded. However in the future there may be aTokens that allow for example to stake the underlying
* to receive LM rewards. In that case, `handleRepayment()` would perform the staking of the underlying asset.
It is likely that a staking implementation of the kind described would stake for user (the sender) when it should stake
for params.onBehalfOf (the borrower).
