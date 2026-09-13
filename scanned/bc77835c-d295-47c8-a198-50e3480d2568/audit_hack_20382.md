# [M] 5.3.3 YieldManagercan claim fewer unstaked tokens than expected resulting in insolvency

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** YieldManager.sol#L

**Description:** When unstaking from Lido the funds are pending in Lido's withdrawal queue and need to be claimed
later. The claimed amount can at the time of claiming be less than the requested amount (due to negative rebases),
seeWithdrawalQueueBase._calculateClaimableEther:

```
if (batchShareRate > checkpoint.maxShareRate) {
eth = shares * checkpoint.maxShareRate / E27_PRECISION_BASE;
}
```
TheYieldManagerwill first increase thependingBalancebyamountinunstakeand then decrease the amount by
claimedinclaimPending. In caseclaimed < amount, the accounting is wrong as the contract still thinks it would
receive apendingBalanceofamount - claimed. The pending balance for this withdrawal needs to be cleared
such thattotalValueis correctly tracked and not overestimated. In addition, the loss needs to be accounted for
in theunstakefunction to not be insolvent for L2 withdrawals (becausetotalValue()decreased).

**Recommendation:** The pending balance for this claim needs to be cleared and the loss ofrequestedUnstake -
claimedUnstakemust be booked. Ideally, the entire insurance fund logic ofcommitYieldReportwould run as well
for this loss.

```
// pseudo code, should be verified with tests
```
```
// in YM.claimPending, we don't track all of these vars yet
// reduce pending balance by initial request amount
YieldProvider(providerAddress).recordClaimed(unstakeRequest.requestedAmount);
// book difference as a loss
// ideally this would run the insurance code again, and cover losses if called with enableInsurance
accumulatedNegativeYields += (unstakeRequest.requestedAmount - unstakeRequest.claimedAmount);
```
