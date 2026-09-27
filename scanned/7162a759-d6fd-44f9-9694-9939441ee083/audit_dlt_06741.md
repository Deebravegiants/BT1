# [M] Quorum could be less than intended

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-nouns-builder
Published: 2022-09-11
Source: https://github.com/code-423n4/2022-09-nouns-builder-findings/issues/195
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-09-nouns-builder/blob/7e9fddbbacdd7d7812e912a369cfd862ee67dc03/src/governance/governor/Governor.sol#L475
https://github.com/code-423n4/2022-09-nouns-builder/blob/7e9fddbbacdd7d7812e912a369cfd862ee67dc03/src/governance/governor/Governor.sol#L462


# Vulnerability details

## Impact
There could be tokens minted between the `quorum` computation and the vote, which would lead to a quorum lower than intended. It could be an issue at the beginning of the `Token` lifecycle, when the total supply is still low.

## Proof of Concept
When creating a proposal in the `Governor` contract, [`proposal.quorumVotes`](https://github.com/code-423n4/2022-09-nouns-builder/blob/7e9fddbbacdd7d7812e912a369cfd862ee67dc03/src/governance/governor/Governor.sol#L168) is computed during the `propose` tx. However tokens could be minted after the `propose` in the same block. In this case, they'll still have a vote during the proposal due to how [`token.getPastVotes`](https://github.com/code-423n4/2022-09-nouns-builder/blob/7e9fddbbacdd7d7812e912a369cfd862ee67dc03/src/governance/governor/Governor.sol#L462) works, therefore the quorum will be lower than intended given the actual total supply.

## Recommended Mitigation Steps
Either compute the total supply afterwards, for example at the beginning of the vote, either takes the vote with a timestamp of `proposal.timeCreated` - 1 to not count the block during which the tx was submitted.
