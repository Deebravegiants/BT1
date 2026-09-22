# [M] CAP_PER_ADDRESS can be bypassed by subcontracts

## Summary
Severity: Medium
Reporter: kutugu
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L143
Type: audit-issue

## Details
# CAP_PER_ADDRESS can be bypassed by subcontracts

## Summary

CAP_PER_ADDRESS can be bypassed by subcontracts, by creating multiple subcontracts, each contract can mint CAP_PER_ADDRESS  NFTs and transfer them to the owner in one tx. 
For popular NFT, there is definitely value to do so. In fact, this is a common problem in popular NFT mint, and only limiting CAP_PER_ADDRESS doesn't make any sense. The `msg.sender` must also be restricted to EOA.

## Vulnerability Detail

```solidity
        // Cache mintedPerAddressBefore to save on sloads
        uint256 mintedPerAddressBefore = mintedPerAddress[msg.sender];

        // Cannot mint more than the cap per address
        require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
```

For reasons explained above, the msg.sender restriction can be bypassed by creating multiple subcontracts.

## Impact

CAP_PER_ADDRESS can be bypassed by subcontracts

## Code Snippet

- https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L143

## Tool used

Manual Review

## Recommendation

Limit msg.sender is an EOA.
