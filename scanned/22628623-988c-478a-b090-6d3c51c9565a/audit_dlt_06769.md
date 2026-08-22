# [H] The quorumVotes can be bypassed

## Summary
Severity: High
Chain: Smart contract
Component: 2023-12-revolutionprotocol
Published: 2023-12-21
Source: https://github.com/code-423n4/2023-12-revolutionprotocol-findings/issues/409
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-12-revolutionprotocol/blob/08ff070da420e95d7c7ddf9d068cbf54433101c4/packages/revolution/src/CultureIndex.sol#L209-L234


# Vulnerability details

## Impact

This vulnerability allows for the minting and auctioning of an art piece that has not met the required quorum. It enables malicious voters to influence outcomes with fewer votes than what is stipulated by the protocol. This undermines a key invariant of the protocol:

        An art piece that has not met quorum cannot be dropped.

https://github.com/code-423n4/2023-12-revolutionprotocol/blob/08ff070da420e95d7c7ddf9d068cbf54433101c4/README.md?plain=1#L291

## Proof of Concept

The `quorumVotes` for an art piece are calculated at its creation as a fraction of the `totalVotesSupply`, which depends on the total supply of `erc20VotingToken` and `erc721VotingToken`:
        
        (quorumVotesBPS * newPiece.totalVotesSupply) / 10_000.

```javascript
File: src/CultureIndex.sol
209:     function createPiece(
210:         ArtPieceMetadata calldata metadata,
211:         CreatorBps[] calldata creatorArray
212:     ) public returns (uint256) {
213:         uint256 creatorArrayLength = validateCreatorsArray(creatorArray);
214: 
215:         // Validate the media type and associated data
216:         validateMediaType(metadata);
217: 
218:         uint256 pieceId = _currentPieceId++;
219: 
220:         /// @dev Insert the new piece into the max heap
221:         maxHeap.insert(pieceId, 0);
222: 
223:         ArtPiece storage newPiece = pieces[pieceId];
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-12-revolutionprotocol-findings/issues/409_
