# [M] Mitigation Confirmed for Mitigation of M-05: See comments

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/64
Type: code-finding

## Details
## Mitigated issue
[M-05: Missing derivative limit and deposit availability checks will revert the whole stake() function](https://github.com/code-423n4/2023-03-asymmetry-findings/issues/812)

The issue was that `stake()` calls `deposit()` on each derivative without considering certain conditions under which some `deposit()` might revert.
There is an overlap between this issue and [M-06: DoS due to external call failure](https://github.com/code-423n4/2023-03-asymmetry-findings/issues/770). M-06 simply pertains to the optimistic dependence on the success of each `deposit()` in `SafeEth` functions, while this issue, M-05, pertains to the lack of checks within `deposit()`. This distinction only matters in practice if there is a choice to be made in the case of a failed check, rather than just reverting. `WstEth.deposit()` and `SfrxEth.deposit()` didn't (and don't) offer an alternative to reverting, so with regards to these M-05 and M-06 are in practice the same issue.
`Reth.deposit()` did offer an alternative, however. There it was checked whether Rocket Pool can be deposited into, or, failing that, using Uniswap. The issue was that one specific check was missing, so `Reth.deposit()` might try to deposit into Rocket Pool when this is in fact not possible, and thus revert, which reverts the entire `stake()`.

## Mitigation review
The deposit path fallback in `Reth.deposit()` has been removed. Now only Balancer is used. Therefore this part of the issue is moot.
However, M-06, which has not been mitigated (OoS), subsumes M-05, so the remaining part of the issue has not been resolved. If it is considered that Balancer is the best and only viable choice, then there is no point of having a fallback option, and therefore there is no point in checking first whether it would fail, which is to say that a mitigation of M-05 would be pointless.
In conclusion, if it is decided that each `deposit()` should only have a single option for depositing, and that M-06 should not be mitigated, then M-05 requires no further action. But technically this issue has not been mitigated.
