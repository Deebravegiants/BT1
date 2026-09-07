# [C] Attackers can control the vote result and ampli...

## Summary
Severity: Critical
Chain: Smart contract
Component: ZeroLend
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/28912%20-%20%5BSC%20-%20Critical%5D%20Attackers%20can%20control%20the%20vote%20result%20and%20ampli....md
Type: immunefi-boost

## Details
Target: https://github.com/zerolend/governance

## Description

## Brief/Intro

There is on lock on `PoolVoter.sol`. The voting results can be manipulated by repeatedly staking and unstaking in OmnichainStaking.

## Vulnerability Details

Users can obtain NFTs by locking their zero tokens in either `lockerLp` or `lockerToken`. After acquiring the NFT, they can stake it in the `OmnichainStaking` to earn the corresponding token. Subsequently, they gain the ability to vote through PoolVoter, allowing them to control the share of the respective pool. When users vote, the PoolVoter.sol directly uses their balance in OmnichainStaking to determine their voting weight.

```
    function _vote(
        address _who,
        address[] memory _poolVote,
        uint256[] memory _weights
    ) internal {
        // require(ve(_ve).isApprovedOrOwner(msg.sender, _tokenId));
        _reset(_who);
        uint256 _poolCnt = _poolVote.length;
        uint256 _weight = staking.balanceOf(_who);
        uint256 _totalVoteWeight = 0;
        uint256 _usedWeight = 0;
```

Although there are some checks in OmnichainStaking to avoid transfer between users

```
    function transfer(address, uint256) public pure override returns (bool) {
        // don't allow users to transfer voting power. voting power can only
        // be minted or burnt and act like SBTs
        require(false, "transfer disabled");
        return false;
    }

    function transferFrom(
        address,
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/28912%20-%20%5BSC%20-%20Critical%5D%20Attackers%20can%20control%20the%20vote%20result%20and%20ampli....md_
