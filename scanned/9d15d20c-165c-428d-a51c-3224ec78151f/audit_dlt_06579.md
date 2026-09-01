# [M] in `setVoteDelay::vote` Users opted to vote for Killed Gauages will be forced to voting Delays.

## Summary
Severity: Medium
Chain: Smart contract
Component: Fenix-
Published: 2024-07-22
Source: https://github.com/hats-finance/Fenix--0x9d7765a7ebd5b6322a30797a44a5428531970d3d/issues/62
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** ililhunterlili
**Submission hash (on-chain):** 0x2abf270b24997b728ee03c9597b032a82888702290ef262f27e2d1709e505856
**Severity:** medium

**Description:**
**Description**\

first of all we have to take into considerations that `VOTE_DELAY` can be at `MAX_VOTE_DELAY` due to this check

```solidity
    function setVoteDelay(uint256 _delay) external VoterAdmin {
        require(_delay != VOTE_DELAY, "already set");
        require(_delay <= MAX_VOTE_DELAY, "max delay"); <<@
        emit SetVoteDelay(VOTE_DELAY, _delay);
        VOTE_DELAY = _delay;
    }
```
taking into considerations that `VOTE_DELAY` may be actually 1 Week then we see that at 

```solidity
    function vote(uint256 _tokenId, address[] calldata _poolVote, uint256[] calldata _weights) external nonReentrant {
        _voteDelay(_tokenId);
        require(IVotingEscrow(_ve).isApprovedOrOwner(msg.sender, _tokenId), "!approved/Owner");
        require(_poolVote.length == _weights.length, "Pool/Weights length !=");
        _vote(_tokenId, _poolVote, _weights);
        lastVoted[_tokenId] = _epochTimestamp() + 1; <<@
    }
```
we set `lastVoted` to the start of the current epoch

the problem rises from the fact that users unintentially may vote for killed `Gauges` without knowing that they are killed and in `_vote` there is no check for reverts for current scenario

```solidity
    function _vote(uint256 _tokenId, address[] memory _poolVote, uint256[] memory _weights) internal {
......    SKIP

        for (uint i = 0; i < _poolCnt; i++) {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Fenix--0x9d7765a7ebd5b6322a30797a44a5428531970d3d/issues/62_
