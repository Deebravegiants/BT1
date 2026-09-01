# [C] Manipulation of governance voting result by unl...

## Summary
Severity: Critical
Chain: Smart contract
Component: Alchemix
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30925%20-%20%5BSC%20-%20Critical%5D%20Manipulation%20of%20governance%20voting%20result%20by%20unl....md
Type: immunefi-boost

## Details
Target: https://github.com/alchemix-finance/alchemix-v2-dao/blob/main/src/Voter.sol

## Description

## Description

### Brief/Intro

Flux token implements a standard ERC20 token with extra features. Flux tokens are accrued by users of VotingEscrow when voting in the contract Voter. Flux tokens can be used to: i) exit a ve-position early by paying a penalty fee when calling function startCooldown, ii) boost voting power of a NFT holder in contract Voter, or iii) as a normal ERC20 token that can be traded in other systems.

So Flux tokens can be used to boost the voting power of a NFT holder. It is shown in the code of vote() function as below.

https://github.com/alchemix-finance/alchemix-v2-dao/blob/main/src/Voter.sol#L228C5-L233C6

```solidity
function vote(
        uint256 _tokenId,
        address[] calldata _poolVote,
        uint256[] calldata _weights,
        uint256 _boost
    ) external onlyNewEpoch(_tokenId) { {

        // redacted for simplicity

    }
    _vote(_tokenId, _poolVote, _weights, _boost);

```

https://github.com/alchemix-finance/alchemix-v2-dao/blob/main/src/Voter.sol#L412-L455

```solidity
function _vote(uint256 _tokenId, address[] memory _poolVote, uint256[] memory _weights, uint256 _boost) internal {
        
        
        // redacted for simplicity

        IFluxToken(FLUX).accrueFlux(_tokenId);
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30925%20-%20%5BSC%20-%20Critical%5D%20Manipulation%20of%20governance%20voting%20result%20by%20unl....md_
