# [H] NFTExchange contract is unable to receive NFTs of any kind

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-06
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/10
Type: hats-finding

## Details
**Github username:** --
**Submission hash (on-chain):** 0x1e594f92fde0c1e75fa6282565f3fbe46d7ec1988b7a969ea38a8d9be1a913c3
**Severity:** high

**Description:**
**Description**\
As discussed with the sponsers, `NFTExchange` contract is supposed to receive and hold the nfts but it does not have the onreceive function for erc721  and will not be able to receive the nfts.

**Attack Scenario**\
NFTExchange.sol essentially works like a wallet

As intended this contract will receive nfts, from owner. However, as it is currently implemented the contract will not be able to receive NFTs sent with safeTransferFrom(), because it do not implement the necessary functions to safely receive these tokens..

you can see it here
https://eips.ethereum.org/EIPS/eip-721

search for this line on the above website and you will find it

`A wallet/broker/auction application MUST implement the wallet interface if it will accept safe transfers.`



**Attachments**

https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/master/src/NFTExchange.sol#L51


implement the onERC721Received() functions in code
