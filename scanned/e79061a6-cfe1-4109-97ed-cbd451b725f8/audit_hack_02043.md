# [H] 6.2 Multiple Votes by Delegation

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design High Version 1 Code Corrected

Upon VotingWeightproxy.announceUnlock and VotingWeightproxy.unlock, no check is
done to verify that the voting agent is not currently locking the delegated amount. This enables an attack
where it is possible to vote multiple times with the same Q.

Here is the attack scenario: A i and V i are accounts controlled by attacker.

```
1.A i : QVault.lock(X)
2.A i : VWP.announceNewVotingAgent(V1) and VWP.setNewVotingAgent, can do it in one go
because getLockeduntil will return 0 since A i did not vote
3.V i : vote on proposal, gets a lock on its own lockInfo
```
```
4.A i : QVault.announceUnlock(X) and QVault.unlock(X), can do it in one go since A i did not vote
(no lock)
5.A i : Qvault.transfer(A i+1, X)
6.goto 1. with i = i+
```
Code corrected :

Lock time is now tracked only once per user, previously it was once per locking contract and per user.
Now both announceUnlock and unlock now take into account the max time between user's own time
lock and its voting agent's time lock, this mitigates the attack described above.
