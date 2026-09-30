# [H] H-02 | Reorgs Invalidate The Locked Invariant

## Summary
Severity: High
Contest weight: 0.1880
Dataset id: 2007
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
function releaseOnEid() transfers token from origin chain owner to the Beacon.sol contract, then delegates the rights to the owner, completing the lzSend() -> lzReceive() request on the destination chain. For completed request the NFTShadow is minted and is now owned by the beneficiary on the destination chain. In the case of a reorg on the base chain, the NFT ownership will revert back to the original owner, become unlocked on the origin chain and the destination chain. Example:
1. Owner 0xA bridges BAYC ID:11 to polygon
Chain:
ETH
NFT:
BAYC
Owner:
Beacon
Delegate:
0xA
Block:
Chain:
Polygon
NFT:
BAYC Shadow
Owner:
0xA
Block:
2. 0xA transfers to 0xB on polygon
Chain:
ETH
NFT:
BAYC
Owner:
Beacon
Block:
Chain:
Polygon
NFT:
BAYC Shadow
Owner:
0xB
Block:

## Recommendation
No data
