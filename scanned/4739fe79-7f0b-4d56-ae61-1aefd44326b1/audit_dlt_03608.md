# [M] `manuallyRemoveBallot()` doesn't check if the ballot can be finalized or has been removed before

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-saltyio-mitigation
Published: 2024-03-06
Source: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/82
Type: code-finding

## Details
# Lines of code

https://github.com/othernet-global/salty-io/blob/758349850a994c305a0ab9a151d00e738a5a45a0/src/dao/DAO.sol#L271-L279
https://github.com/othernet-global/salty-io/blob/758349850a994c305a0ab9a151d00e738a5a45a0/src/dao/Proposals.sol#L131-L153


# Vulnerability details

# Comments
In the original implementation, a ballot cannot be closed or canceled without meeting the required quorum, even if the `ballotMinimumEndTime` has passed.

# Mitigation
[commit 7583498](https://github.com/othernet-global/salty-io/commit/758349850a994c305a0ab9a151d00e738a5a45a0)
The mitigation introduced a variable `ballotMaximumDuration` for ballot and a function `DAO#manuallyRemoveBallot()`. 
Whenever a ballot is expired, it can be removed by any one. 

# Impact
Three new issues were produced due to missing status checks:
1. Two or more living ballots with the same name can exist at the same time
2. One eligible user can create multi ballots at the same time
3. A ballot could be removed accidentally or intentionally even it has sufficient votes

# Proof of Concept
- Issue 1:
  - Alice created ballotA, which was expired without enough votes
  - ballotA was removed by calling `DAO#manuallyRemoveBallot()`
  - Alice created ballotB
  - Alice called `DAO#manuallyRemoveBallot()` to remove ballotA again. `_userHasActiveProposal[Alice]` was reset to `false`
  - Alice created ballotC successfully even ballotB is living.
- Issue 2: 
  - Alice created ballotA(ballotID = A1), which was expired without enough votes
  - The ballotA was removed by calling `DAO#manuallyRemoveBallot()`
  - Alice created ballotA(ballotID = A2) again (same ballot name but different ballotID)
  - Bob called `DAO#manuallyRemoveBallot(A1)` to remove ballot again, `openBallotsByName[ballotA]` was deleted
  - Bob created ballotA successfully even Alice's ballotA is opened.
- Issue 3:
  - Alice creates a new ballot with `ballotMinimumDuration` as 10 days and `ballotMaximumDuration` as 30 days
  - The voting number is very closed to `requiredQuorum`

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/82_
