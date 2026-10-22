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
181     * are aware of the ERC721 protocol to prevent tokens from being forever locked.


193     * - If `to` refers to a smart contract, it must implement {IERC721Receiver-onERC721Received}, which is called upon a safe transfer.
```

3) OpenZeppelin’s documentation discourages the use of transferFrom(), Use safeTransferFrom() whenever possible,

Openzeppelin warns of using transfer( ) by saying,

> "Note that the caller is responsible to confirm that the recipient is capable of receiving ERC721 or else they may be permanently lost. Usage of safeTransferFrom prevents loss, though the caller must understand this adds an external call which potentially creates a reentrancy vulnerability."

Also, As per the documentation of EIP-721:

> A wallet/broker/auction application MUST implement the wallet interface if it will accept safe transfers.

Reference: https://eips.ethereum.org/EIPS/eip-721

However, `owner()` is hardcoded and there is no parameter to put the recipient address in buy function.

This issue is categorised as Medium severity as it is breaking the intended functionality of etherFi contract and due to loss of ERC721 tokens or assets.

**Attack Scenario**\

When the `buy()` function is called by reserved buyer to purchase membership NFT by giving his t-NFT, the t-NFT can be locked or frozen with recipient address if the recipient address does not have support of `onERC721Received` support to receive the ERC721 tokens i.e T-NFT in our case.

**Attachments**

1. **Proof of Concept (PoC) File**

https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/NFTExchange.sol#L94

2. **Revised Code File (Optional)**

As openzeppelin recommended to use safeTransferFrom instead of transferFrom while transferring the ERC721 NFTs. We recommend same so that there should not be loss of assets of reserved buyers.

Below is the high level recommendation to resolve the issue,

```diff

    function buy(uint256[] calldata _tnftTokenIds, uint256[] calldata _mNftTokenIds) external nonReentrant {
        require(_tnftTokenIds.length == _mNftTokenIds.length, "Input arrays must be the same length");
        for (uint256 i = 0; i < _mNftTokenIds.length; i++) {
            uint256 tnftTokenId = _tnftTokenIds[i];
            uint256 mNftTokenId = _mNftTokenIds[i];

            require(reservedBuyers[mNftTokenId] != address(0), "Token is not currently listed for sale");
            require(msg.sender == reservedBuyers[mNftTokenId], "You are not the reserved buyer");
            require(tnftTokenId == targetTNftTokenIds[mNftTokenId], "The T-NFT is not the target");

            require(nodesMgr.phase(tnftTokenId) == IEtherFiNode.VALIDATOR_PHASE.LIVE, "The validator is not LIVE");

            reservedBuyers[mNftTokenId] = address(0);
            targetTNftTokenIds[mNftTokenId] = 0;

-            tNft.transferFrom(msg.sender, owner(), tnftTokenId);
+            tNft.safeTransferFrom(msg.sender, owner(), tnftTokenId);
            membershipNft.safeTransferFrom(address(this), msg.sender, mNftTokenId, 1, "");
        }
    }
```
