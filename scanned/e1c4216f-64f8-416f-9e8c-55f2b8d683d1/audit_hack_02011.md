# [M] 6.4 ForceWithdrawal Needs Prior Approval

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected Specification Changed

In the case that a user believes they are censored, the user can initiate the withdrawal using the
forceWithdraw function of the L1DAIBridge. When the L2 network works as expected, the withdrawal
request is handled.

This however has some prerequisites:

```
1.The user needs to have registered his L1 address in the L2 registry prior to initiating
forceWithdraw(). Note that this may no longer be possible when the L2 network is censoring
transactions hence this should be done by the users before receiving DAI on L2.
2.The execution of finalize_force_withdrawal on L2 in case the Layer2 network complies
requires that the user has previously given allowance to the l2_dai_bridge. Again, giving the
approval at this point in time may no longer be possible in case the L2 network censors
transactions.
```

```
# check allowance
let (contract_address) = get_contract_address()
let (allowance : Uint256) = IDAI.allowance(dai, source, contract_address)
let (allowance_check) = uint256_le(amount, allowance)
if allowance_check == 0:
return ()
end
```
This requirement is not documented and may come as a surprise for the user. Note that for normal
withdrawals from L2 using withdraw no such allowance is needed. Furthermore without the check in
finalize_force_withdrawal the withdrawal / burning of the DAI would work as the
l2_dai_bridge is a ward in the DAI contract and has the privilege to burn the DAI of any address
without the need for an approval.

The case that the L2 network may only censors transactions other than forced withdrawals (in order to
avoid detection of the misbehavior) and its implication must be considered.

Overall the ForcedWithdrawal process and it's restrictions is not documented enough.

Code corrected and specification changed:

Issue 1) was addressed by improving the documentation. The documentation now clearly states what
actions are required before a forced withdrawal can be executed. The enhanced documentation also
resolves 2), note that in the updated code a ward of the DAI contract no longer has the privilege to burn
DAI and hence the approval is needed. It's important to understand why
finalize_force_withdrawal must check whether the approval exists: Burning without the
allowance would result in the transaction to revert. The prover can't prove failed executions, reverts are
indistinguishable from censored messages. By checking the allowance and gracefully terminate the
transaction when no sufficient allowance exist, the transaction can be executed. Hence the message
from L1 can be processed which allows to clear the message in the StarkNet contract on Ethereum. This
proves that the transaction must have been executed on L2.
