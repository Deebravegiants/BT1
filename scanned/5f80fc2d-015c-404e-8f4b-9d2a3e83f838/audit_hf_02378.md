# [M] Improved Handling of Caller Fees in _resetVotes()

## Summary
Severity: Medium
Contest weight: 0.4421
Dataset id: 12837
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the WombatVoterProxy contract, in order to incentivize the caller to cast the pending votes to Wombat, it rewards the caller with the caller fees from the received bribe rewards. The caller fees are sent to the BribeManager contract which further forwards them to the caller. In particular, if no caller is specified in the WombatVoterProxy::vote() routine, no caller fee is rewarded. While reviewing the logic to remove all votes from all pools, we notice the caller is specified but the caller fees are not handled.
To elaborate, we show below the code snippet of the _resetVotes() routine, which is used by the owner to remove all votes from all the supported pools. It specifies the caller as the owner itself. However, after invoking the voterProxy.vote() routine (line 198), it does not properly handle the received caller fees which shall be forwarded to the caller (the owner in this case). As a result, the caller fees are locked in the contract. Based on this, it's suggested to not specify the caller or properly transfer the received caller fees to the caller.
```solidity
function _resetVotes() internal {
    uint256 length = pools.length;
    address[] memory lpVote = new address[](length);
    int256[] memory votes = new int256[](length);
    address[] memory rewarders = new address[](length);
    for (uint256 i; i < length; i++) {
        Pool memory pool = poolInfos[pools[i]];
        lpVote[i] = pool.lpToken;
        votes[i] = -int256(getVeWomVoteForLp(pool.lpToken));
        rewarders[i] = pool.rewarder;
    }
    voterProxy.vote(lpVote, votes, rewarders, owner());
    emit AllVoteReset();
}
```

## Recommendation
Revisit the above _resetVotes() routine to not specify the caller or properly transfer the caller fees to the specified caller.
