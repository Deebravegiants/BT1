# [C] Wrong calculation of boost amount in Voterpoke

## Summary
Severity: Critical
Chain: Smart contract
Component: Alchemix
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30814%20-%20%5BSC%20-%20Critical%5D%20Wrong%20calculation%20of%20boost%20amount%20in%20Voterpoke.md
Type: immunefi-boost

## Details
Target: https://github.com/alchemix-finance/alchemix-v2-dao/blob/main/src/Voter.sol

## Description

## Brief/Intro

The Voter.poke function votes again with the same weights, effectively renewing the previous vote. However, the boost value reflected in the previous weights will not be taken into account when the poke function is called. The boost is always 0.

## Vulnerability Details

```
/// @inheritdoc IVoter
    function poke(uint256 _tokenId) public {
        // Previous boost will be taken into account with weights being pulled from the votes mapping
        uint256 _boost = 0;

        if (msg.sender != admin) {
            require(IVotingEscrow(veALCX).isApprovedOrOwner(msg.sender, _tokenId), "not approved or owner");
        }

        address[] memory _poolVote = poolVote[_tokenId];
        uint256 _poolCnt = _poolVote.length;
        uint256[] memory _weights = new uint256[](_poolCnt);

        for (uint256 i = 0; i < _poolCnt; i++) {
            _weights[i] = votes[_tokenId][_poolVote[i]];
        }

        _vote(_tokenId, _poolVote, _weights, _boost);
    }
```

`// Previous boost will be taken into account with weights being pulled from the votes mapping` Will the calculation be done like this explanation? The answer is `No`.

```
_weights[i] = votes[_tokenId][_poolVote[i]];
```


_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30814%20-%20%5BSC%20-%20Critical%5D%20Wrong%20calculation%20of%20boost%20amount%20in%20Voterpoke.md_
