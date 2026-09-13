# [C] \[C01\] Supply is manipulable

## Summary
Severity: Critical
Source: https://github.com/pooltogether/pods/blob/8041b3dc72efd02b94d49fb37b9b308603af5ce/contracts/Pod.sol#L184-L185
Type: audit-issue

## Details
When a user deposits collateral, the total supply and their individual balance [are scheduled to be updated](https://github.com/pooltogether/pods/blob/8041b3dc72efd02b94d49fb37b9b308603af5ce/contracts/Pod.sol#L184-L185) in the next draw. However, if the collateral is withdrawn before the next round, [the user’s individual balance is updated](https://github.com/pooltogether/pods/blob/8041b3dc72efd02b94d49fb37b9b308603af5ce/contracts/Pod.sol#L292) but the supply is not.

When the [supply is consolidated](https://github.com/pooltogether/pods/blob/8041b3dc72efd02b94d49fb37b9b308603af5ce/contracts/Pod.sol#L444), additional Pod tokens will be minted that are not assigned to any user.

Subsequently, when the pod wins a lottery, the new Pool tokens will be spread evenly over all Pod tokens, even the ones that are unassigned. This means that users will receive less than their fair share of the winnings.

Consider updating the scheduled supply when withdrawing a pending deposit. More generally, consider abstracting the interaction with scheduled user balances and supply so they are both updated with the same call.

**Update:** _Fixed in [PR#2](https://github.com/pooltogether/pods/pull/2/). The supply is updated when withdrawing a pending deposit._
