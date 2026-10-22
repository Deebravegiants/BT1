# [M] MerkleReserveMinter minting methodology

## Summary
Severity: Medium
Contest weight: 0.5941
Dataset id: 20336
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
MerkleReserveMinter allows large number of tokens to be minted instantaneously which is incompatible with the current governance structure which relies on tokens being minted individually and time locked after minting by the auction. By minting and creating a proposal in the same block a user is able to create a proposal with significantly lower quorum than expected. This could easily be used to hijack the migrated DAO.
MerkleReserveMinter.sol#L154-L167
```solidity
unchecked {
    for (uint256 i = 0; i < claimCount; ++i) {
        // Load claim in memory
        MerkleClaim memory claim = claims[i];
        // Requires one proof per tokenId to handle cases where users want to partially claim
        if (!MerkleProof.verify(claim.merkleProof, settings.merkleRoot, keccak256(abi.encode(claim.mintTo, claim.tokenId)))) {
            revert INVALID_MERKLE_PROOF(claim.mintTo, claim.merkleProof, settings.merkleRoot);
        }
        // Only allowing reserved tokens to be minted for this strategy
        IToken(tokenContract).mintFromReserveTo(claim.mintTo, claim.tokenId);
    }
}
```
When minting from the claim merkle tree, a user is able to mint as many tokens as they want in a single transaction. This means in a single transaction, the supply of the token can increase very dramatically. Now we'll take a look at the governor contract as to why this is such an issue.
Governor.sol#L184-L192
```solidity
// Store the proposal data
proposal.voteStart = SafeCast.toUint32(snapshot);
proposal.voteEnd = SafeCast.toUint32(deadline);
proposal.proposalThreshold = SafeCast.toUint32(currentProposalThreshold);
proposal.quorumVotes = SafeCast.toUint32(quorum());
proposal.proposer = msg.sender;
proposal.timeCreated = SafeCast.toUint32(block.timestamp);
emit ProposalCreated(proposalId, _targets, _values, _calldatas, _description, descriptionHash, proposal);
```
Governor.sol#L495-L499
```solidity
function quorum() public view returns (uint256) {
    unchecked {
        return (settings.token.totalSupply() * settings.quorumThresholdBps) / BPS_PER_100_PERCENT;
    }
}
```
When creating a proposal, we see that it uses a snapshot of the CURRENT total supply. This is what leads to the issue. The setup is fairly straightforward and occurs all in a single transaction:
1) Create a malicious proposal (which snapshots supply)
2) Mint all the tokens
3) Vote on malicious proposal with minted tokens
The reason this works is because the quorum is based on the supply before the mint while votes are considered after the mint, allowing significant manipulation of the quorum. DOA can be completely hijacked

## Recommendation
Token should be changed to use a checkpoint based total supply, similar to how balances are handled. Quorum should be based on that instead of the current supply.
