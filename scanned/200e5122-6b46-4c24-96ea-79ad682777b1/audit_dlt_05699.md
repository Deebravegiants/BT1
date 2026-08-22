# [C] Voterpoke can be called at will leading to a us...

## Summary
Severity: Critical
Chain: Smart contract
Component: Alchemix
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30906%20-%20%5BSC%20-%20Critical%5D%20Voterpoke%20can%20be%20called%20at%20will%20leading%20to%20a%20us....md
Type: immunefi-boost

## Details
Target: https://github.com/alchemix-finance/alchemix-v2-dao/blob/main/src/Voter.sol

## Description

## Brief/Intro

After a user votes, they can call poke however many times they want. This accrues Flux each time it recasts their vote. Giving them access to either Ragequit and withdraw early or leave the unclaimed flux and max boost their future votes, as well as walk away with leftover Flux tokens.

## Vulnerability Details

Once a user votes, they cannot vote again until the next epoch. However `Voter.poke()` can be called at any time. In the `poke` function `_vote` is called.

In `_vote` there is a call to the flux token contract that accrues unclaimed Flux.

```
...
    _reset(_tokenId);

        uint256 _poolCnt = _poolVote.length;
        uint256 _totalVoteWeight = 0;
        uint256 _totalWeight = 0;

        for (uint256 i = 0; i < _poolCnt; i++) {
            _totalVoteWeight += _weights[i];
        }

        IFluxToken(FLUX).accrueFlux(_tokenId);
...
```

This accrues the unclaimed Flux balance of the \_tokenId by the amount of `claimableFlux` received from the VotingEscrow.sol contract

```
function claimableFlux(uint256 _tokenId) public view returns (uint256) {
        // If the lock is expired, no flux is claimable at the current epoch
        if (block.timestamp > locked[_tokenId].end) {
            return 0;
        }
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30906%20-%20%5BSC%20-%20Critical%5D%20Voterpoke%20can%20be%20called%20at%20will%20leading%20to%20a%20us....md_
