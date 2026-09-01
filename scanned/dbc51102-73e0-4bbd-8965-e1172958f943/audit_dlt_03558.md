# [M] Raffle creator can rug participants

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-12-forgeries
Published: 2022-12-14
Source: https://github.com/code-423n4/2022-12-forgeries-findings/issues/88
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-12-forgeries/blob/fc271cf20c05ce857d967728edfb368c58881d85/src/VRFNFTRandomDraw.sol#L173
https://github.com/code-423n4/2022-12-forgeries/blob/fc271cf20c05ce857d967728edfb368c58881d85/src/VRFNFTRandomDraw.sol#L304
https://github.com/code-423n4/2022-12-forgeries/blob/fc271cf20c05ce857d967728edfb368c58881d85/src/VRFNFTRandomDraw.sol#L127


# Vulnerability details

## Impact
The raffle creator is not required to actually give the NFT away. The NFT that is used for the raffle is transferred to the contract when `startDraw` is executed. Before that, the NFT is in the hands of the creator. This means that he might create a raffle to make users buy NFTs required to participate and then refuse to draw a winner and keep the NFT to himself. Furthermore, he might not even be the owner of NFT in the first place, which he can achieve by flash loaning the NFT in order to pass the `ownerOf` check in `initialize` function.

## Proof of Concept
### Example 1
1. User U creates an NFT collection C
2. He buys a BAYC NFT
3. He creates a raffle with it, and requires `drawingToken` to be from collection C
4. Users buy tokens from his collection C
5. He then refuses to execute `startDraw` function and rather sells the BAYC NFT

### Example 2
1. User U creates an NFT collection C
2. User U uses an NFT flash loan to borrow a very expensive NFT
3. In the same transaction he creates a raffle with this NFT, and requires `drawingToken` to be from collection C
4. The check that he is the owner will pass, because for the duration of the transaction he in fact is
5. Users see that there is a raffle for a very expensive NFT, so they buy tokens C
6. The winner is never drawn, because the creator does not even own the NFT

### Example 3
1. User U has an NFT X
2. He puts X on a sale on some NFT marketplace (which does not require him to lock it in contract)
3. He forgets about it and creates a raffle with it
4. Users buy the tokens necessary for the raffle
5. User U wants to execute the `startDraw` function, but just before it the NFT X is bought from him through the marketplace
6. The winner cannot be drawn

## Recommended Mitigation Steps
Transfer the NFT to the contract at the time of creation of the raffle.  You can do that by approving the factory contract to transfer the token and do the transfer in [`makeNewDraw`](https://github.com/code-423n4/2022-12-forgeries/blob/fc271cf20c05ce857d967728edfb368c58881d85/src/VRFNFTRandomDrawFactory.sol#L43) function between cloning and `initialization`.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-12-forgeries-findings/issues/88_
