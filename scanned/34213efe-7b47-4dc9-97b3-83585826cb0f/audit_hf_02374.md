# [H] Sybil Attacks on QuantoSwap Token Voting

## Summary
Severity: High
Contest weight: 0.6403
Dataset id: 12816
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The QuantoSwapToken tokens can be used for governance in allowing for users to cast and record the votes. Moreover, the QuantoSwapToken contract allows for dynamic delegation of a voter to another, though the delegation is not transitive. When a submitted proposal is being tallied, the number of votes are counted via getPriorVotes(). Our analysis shows that the current governance functionality is vulnerable to a new type of so-called Sybil attacks. For elaboration, let's assume at the very beginning there is a malicious actor named Malice, who owns 100 QNS tokens. Malice has an accomplice named Trudy who currently has 0 balance of QNS. This Sybil attack can be launched as follows:
```solidity
function _delegate(address delegator, address delegatee) internal {
    address currentDelegate = _delegates[delegator];
    uint256 delegatorBalance = balanceOf(delegator); // balance of underlying QNSs (not scaled);
    _delegates[delegator] = delegatee;
    emit DelegateChanged(delegator, currentDelegate, delegatee);
    _moveDelegates(currentDelegate, delegatee, delegatorBalance);
}

function _moveDelegates(address srcRep, address dstRep, uint256 amount) internal {
    if (srcRep != dstRep && amount > 0) {
        if (srcRep != address(0)) {
            // decrease old representative
            uint32 srcRepNum = numCheckpoints[srcRep];
            uint256 srcRepOld = srcRepNum > 0 ? checkpoints[srcRep][srcRepNum - 1].votes : 0;
            uint256 srcRepNew = srcRepOld.sub(amount);
            _writeCheckpoint(srcRep, srcRepNum, srcRepOld, srcRepNew);
        }
        if (dstRep != address(0)) {
            // increase new representative
            uint32 dstRepNum = numCheckpoints[dstRep];
            uint256 dstRepOld = dstRepNum > 0 ? checkpoints[dstRep][dstRepNum - 1].votes : 0;
            uint256 dstRepNew = dstRepOld.add(amount);
            _writeCheckpoint(dstRep, dstRepNum, dstRepOld, dstRepNew);
        }
    }
}
```
1. Malice initially delegates the voting to Trudy. Right after the initial delegation, Trudy can have 100 votes if he chooses to cast the vote.
2. Malice transfers the full 100 balance to M1 who also delegates the voting to Trudy. Right after this delegation, Trudy can have 200 votes if he chooses to cast the vote. The reason is that the QuantoSwapToken contract's transfer() does NOT _moveDelegates() together. In other words, even now Malice has 0 balance, the initial delegation (of Malice) to Trudy will not be affected, therefore Trudy still retains the voting power of 100 QNS. When M1 delegates to Trudy, since M1 now has 100 QNS, Trudy will get additional 100 votes, totaling 200 votes.
3. We can repeat by transferring Mi's 100 QNS balance to Mi+1 who also delegates the votes to Trudy. Every iteration will essentially add 100 voting power to Trudy. In other words, we can effectively amplify the voting powers of Trudy arbitrarily with new accounts created and iterated!

## Recommendation
To mitigate, it is necessary to accompany every single transfer() and transferFrom() with the _moveDelegates() so that the voting power of the sender's delegate will be moved to the destination's delegate. By doing so, we can effectively mitigate the above Sybil attacks.
