# [M] Duplicate Chunk IDs

## Summary
Severity: Medium
Contest weight: 0.4277
Dataset id: 15056
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In ChunkProcessor, the chunk manipulation functions such as pushChunk() will perform a downcast of Chunk ID and Indexes from uint256 to uint32. This effectively reduces the maximum number of chunks to type(uint32).max, As chunks represent the paired/wrapped ERC721, this means that NFT supply based on SFT418 will be similarly capped as well. The issue is that capping of the NFT supply to 32-bit is not compliant with EIP721, which allows up to type(uint256).max NFTs. This is evident from the use of uint256 to represent the account balance in balanceOf(). The implication of this issue is that SFT418 will not function properly when it is used for cases where the number of NFTs exceeds type(uint32).max. That will cause duplication of chunk ID as Chunk ID greater than type(uint32).max will be truncated to 32-bit, violating the non-fungible property.
```solidity
function _pushChunk(address to_, uint256 id_) internal virtual {
    require(to_ != address(0), "INVALID_TO");
    require(_chunkToOwners[id_].owner == address(0), "CHUNK_EXISTS");
    uint256 _nextIndex = _ownerToChunkIndexes[to_].length;
    _chunkToOwners[id_] = ChunkInfo(
        //@audit index is downcasted to uint32
        uint32(_nextIndex),
        //@audit chunk ID is also downcasted to uint32
        address(0)
    );
    _ownerToChunkIndexes[to_].push(uint32(id_));
}
```

## Recommendation
Either support up to uint256 Chunk ID/Indexes or ensure that chunk ID and total ERC721 supply does not exceed uint32.
