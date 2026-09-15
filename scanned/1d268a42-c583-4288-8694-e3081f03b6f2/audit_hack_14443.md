# [M] Risk of Losing `NFT`s due to the use `mint` instead of `safeMint`.

## Summary
Severity: Medium
Reporter: shealtielanz
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128C3-L169C6
Type: audit-issue

## Details
# Risk of Losing `NFT`s due to the use `mint` instead of `safeMint`.

## Summary
some contracts can't handle `NFT`s, and when `NFT` are minted to them, the `NFT` is lost, this is because of the lack of `ERC721onReciever` Function in them(recipient), to secure against losing `NFT`s like this, The `EIP721` standard stated that before minting or sending `NFT`s to any address the contract should check if the address to receive to is either an `EOA` or a Smart contract if it is a smart contract certain checks should be made in order to know if it can't handle `NFT`s, if it can handle it, the `NFT` can be minted or transfered to it, but if it can't handle `NFT`s, the transaction should be reverted, This is done with the use of safeMint(for minting `NFT`s) and safeTransfer(for transferring `NFT`s). 
However, In the MeritDutchAuction.sol it doesn't implement this safeguard. leading to `NFT`s being lost when minting is done.
## Vulnerability Detail
you can see the [`mint`](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128C3-L169C6) function in `MeritDutchAuction.sol`.
```solidity 
        // Interactions
        for(uint256 i = 0; i < amount; i++) {
            // Mint the amount of NFTs to the sender
            nft.mint(mintedBefore + i + 1, msg.sender);
        }
```
Here it uses `mint`, instead of `safeMint`.
## Impact
This could cause the recipients to lose `NFT`s if their contract can't handle `NFT`s, and when lost it's lost forever.
## Code Snippet
- `Mint` Function ~ [Click here](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128C3-L169C6)
- `Line with Bug` ~ [Click here](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158)
## Tool used

`Manual Review`

## Recommendation
use `safeMint` to mint `Non-Fungible tokens` to participants instead of `mint`.
