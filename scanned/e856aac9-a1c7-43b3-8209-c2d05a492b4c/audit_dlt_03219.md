# [M] Proposal vote power can be easily manipulated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-arcade
Published: 2023-07-28
Source: https://github.com/code-423n4/2023-07-arcade-findings/issues/434
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/ArcadeGSCCoreVoting.sol#L32
https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/external/council/CoreVoting.sol#L172-L181
https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/external/council/CoreVoting.sol#L234-L238


# Vulnerability details

## Impact
`ArcadeGSCCoreVoting` can be a target of vote manipulation: an attacker might be able to take a huge loan (even uncollateralized) for a single block before creating a proposal.

When voting, only this single block is checked when calculating the `votingPower`: this may lead to an attacker being able to execute arbitrary proposals with minimal risks involved.

## Proof of Concept

When a proposal is created, the timestamp registered is the block before the creation. This mitigates flash loan attacks, but it's still possible to manipulate the vote with a normal loan:

```solidity
proposals[proposalCount] = Proposal(
    proposalHash,
    // Note we use blocknumber - 1 here as a flash loan mitigation.
    uint128(block.number - 1), //@audit created
    uint128(block.number + lockDuration),
    uint128(block.number + lockDuration + extraVoteTime),
    uint128(quorum),
    proposals[proposalCount].votingPower,
    uint128(lastCall)
);
```
https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/external/council/CoreVoting.sol#L172-L181

During a `vote`, the `msg.sender` voting power is queried and it will use the previous `created` field:

```solidity
for (uint256 i = 0; i < votingVaults.length; i++) {
    // ensure there are no voting vault duplicates
    for (uint256 j = i + 1; j < votingVaults.length; j++) {
        require(votingVaults[i] != votingVaults[j], "duplicate vault");
    }
    require(approvedVaults[votingVaults[i]], "unverified vault");
    votingPower += uint128(
        IVotingVault(votingVaults[i]).queryVotePower(
            msg.sender,
            proposals[proposalId].created,
            extraVaultData[i]
        )
    );
}
```
https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/external/council/CoreVoting.sol#L234-L238

If the attacker took a huge loan (even uncollateralized) for that single block, they would be able to manipulate the vote with minimal slippage, as it's only one block.

If this happens, they would be able to execute any arbitrary code, if `queryVotePower` depends on the amount of tokens held by the attacker.

## Note about severity

By reading the comments in `ArcadeGSCCoreVoting` it seems that the voting vault used will be the `ArcadeGSCVault`:

```solidity
 * The Arcade GSC Core Voting contract allows members of the GSC vault to vote on and execute proposals
 * in an instance of governance separate from general governance votes.
```

In this case, this issue can't occur, as the `votingPower` does not depend on the amount held by the attacker:

```solidity
// If the address queried is the owner they get a huge number of votes
// This allows the primary governance timelock to take any action the GSC
// can make or block any action the GSC can make. But takes as many votes as
// a protocol upgrade.
if (who == owner) {
    return 100000;
}
// If the who has been in the GSC longer than idleDuration
// return 1 and otherwise return 0.
if (
    members[who].joined > 0 &&
    (members[who].joined + idleDuration) <= block.timestamp
) {
    return 1;
} else {
    return 0;
}    
```
https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/external/council/vaults/GSCVault.sol#L145-L167

However, it's worth noting that this situation might change in the future, as `ArcadeGSCCoreVoting` approved vaults can be multiple, and they are not immutable:

```solidity
/// @notice Updates the status of a voting vault.
/// @param vault Address of the voting vault.
/// @param isValid True to be valid, false otherwise.
function changeVaultStatus(address vault, bool isValid) external onlyOwner {
    approvedVaults[vault] = isValid;
}
```

https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/external/council/CoreVoting.sol#L333-L338

As there are other vaults that use tokens as voting power (e.g [LockingVault](https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/external/council/vaults/LockingVault.sol#L72-L86)), there is a real possibility that this might occur in the future, so I'm flagging it as high severity.


## Tools Used
Manual review

## Recommended Mitigation Steps
Consider using a TWAP to check the voting power of a proposal, instead of checking only the block before the proposal was created.


## Assessed type

Timing
