# [M] If someone becomes GSC member, he may become unkickable forever

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-arcade
Published: 2023-07-28
Source: https://github.com/code-423n4/2023-07-arcade-findings/issues/412
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-arcade/blob/f8ac4e7c4fdea559b73d9dd5606f618d4e6c73cd/contracts/BaseVotingVault.sol#L96-L102
https://github.com/code-423n4/2023-07-arcade/blob/f8ac4e7c4fdea559b73d9dd5606f618d4e6c73cd/contracts/external/council/vaults/GSCVault.sol#L123
https://github.com/code-423n4/2023-07-arcade/blob/f8ac4e7c4fdea559b73d9dd5606f618d4e6c73cd/contracts/external/council/libraries/History.sol#L198-L199
https://github.com/code-423n4/2023-07-arcade/blob/f8ac4e7c4fdea559b73d9dd5606f618d4e6c73cd/contracts/ArcadeGSCVault.sol#L25


# Vulnerability details

*Note: some of the contracts mentioned are out of scope, but the vulnerability exists in the `BaseVotingVault`, which is in-scope, so I argue that the finding is in scope.*

In Arcade ecosystem, there is a GSC group which has some extra privileges like spending some token amount from treasury or creating new proposals in core voting contract.

In order to become a member of this group, user has to have high enough voting power (combined from several voting vaults) and call `proveMembership`. When user's voting power drops beneath a certain threshold, he may be kicked out of the GSC.

`proveMembership` contains the following code:
```solidity
for (uint256 i = 0; i < votingVaults.length; i++) {
            // Call the vault to check last block's voting power
            // Last block to ensure there's no flash loan or other
            // intra contract interaction
            uint256 votes =
                IVotingVault(votingVaults[i]).queryVotePower(
                    msg.sender,
                    block.number - 1,
                    extraData[i]
                );
            // Add up the votes
            totalVotes += votes;
        }
```
So, it basically iterates over all voting vaults that a user specifies, sums up his voting power, and if it's enough, it grants that user a place in GSC.

In order to kick user out from the GSC, the `kick` function may be used and it will iterate over all vaults that were supplied by a user when he called `proveMembership` and if his voting power dropped beneath the threshold, he will be removed from the GSC. `kick` contains the following code:
```solidity
        for (uint256 i = 0; i < votingVaults.length; i++) {
            // If the vault is not approved we don't count its votes now
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-arcade-findings/issues/412_
