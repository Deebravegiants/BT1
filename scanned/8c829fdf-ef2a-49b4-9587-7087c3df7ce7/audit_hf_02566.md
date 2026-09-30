# [H] H-2 Whale governance attack on the protocol takes 1 day and cannot be cancelled by

## Summary
Severity: High
Contest weight: 0.2917
Dataset id: 13785
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The flow of the attack: 1. A whale prepares funds so that the lock for one week gives a weight to bypass the passingPct. 2. In the end of week [N], one minute before week [N+1], the whale calls TokenLocker.lock(week=1). The token locker will register the weight for week [N] 3. Week [N+1] begins in one minute after Step 2. The funds for the attack are unlocked and can be withdrawn. 4. The whale calls AdminVoting.createNewProposal() The payload is the following: – PrismaCore.setGuardian() – Treasury.transferTokens(token=prisma, receiver=whale, amount=everything) 5. The whale calls AdminVoting.voteForProposal() and votes for the proposal from Step 4. AdminVoting uses weights from the previous week [N] which is already finalized and the whale was the largest voter at the end of the week. The whale bypasses passingPct for this proposal, so the proposal can be executed in 1 day. 6. In one day, the whale calls AdminVoting.executeProposal() and withdraws all funds from the Treasury. The guardian cannot cancel this attack. Because the first call in the payload is PrismaCore.setGuardian() which is the only type of call that cannot be cancelled, thus the whole payload cannot be cancelled. • AdminVoting.sol#L193-L196

## Recommendation
We recommend that: • the guardian restriction to cancel PrismaCore.setGuardian() should be fixed. For example, the guardian is not allowed to cancel PrismaCore.setGuardian() only if payload.length == 1. In this case proposers must have only one call in the payload. Otherwise, the guardian can cancel. • when a proposal changes a guardian the protocol can require higher passingPct.
