# [M] `TNFT`can be permanently locked or frozen if transferred to non-implemented `onERC721Received` support contract address in `NFTExchange.sol`

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-07
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/23
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Submission hash (on-chain):** 0x7bed06542227884aaecf5b2b1077a8ca0853b1bc225f6bf457f31338434d1657
**Severity:** medium

**Description:**
**Description**\
`NFTExchange.sol` contract is used for escrowing NFT trades between a multi-sig wallet and a staker.

The contract basically deals with `T-NFTs` and `membershipNft`. There is no issue with `membershipNft` while transferring to recipient, however 
`T-NFTs` have issue while transferring to recipient address. To be noted, `T-NFTs` is an ERC721 token.


The issue is in `buy()` function which allows a reserved buyer to purchase a `membership NFT` with a `T-NFT`.

```Solidity
File: src/NFTExchange.sol

    function buy(uint256[] calldata _tnftTokenIds, uint256[] calldata _mNftTokenIds) external nonReentrant {

            // some code

>>          tNft.transferFrom(msg.sender, owner(), tnftTokenId);
            membershipNft.safeTransferFrom(address(this), msg.sender, mNftTokenId, 1, "");
        }
    }
```


As seen above, transferFrom() method is used while trasferring the `tNft` instead of safeTransferFrom(). I however argue that this isn’t recommended because:

1) The issue is if the recepient is a contract address, the NFT will be locked or frozen because of NO check `OnERC721Received` support in current implementation.

2) Openzeppelin encourages to use safeTransferFrom instead of transferFrom and in ER721.sol, the comment says,

```Solidity
File: contracts/token/ERC721/ERC721.sol

180     * @dev Safely transfers `tokenId` token from `from` to `to`, checking first that contract recipients
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/23_
