# [H] Improper Amount Of Ether Transferred

## Summary
Severity: High
Contest weight: 0.6129
Dataset id: 11814
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.3, each tradable asset is listed for sale in the CogiNFTMarket will be transferred from the owner to the market. Once sold, it will be transferred from the market to the buyer after the listingPrice is collected. And the listingPrice should be paid by the buyer. However, the distribution of the msg.value (transferred in by the buyer) is incorrect.

To elaborate, we show below the purchaseExecution() routine from the CogiNFTMarket contract. This routine checks whether the msg.value equals to the price given by the seller or not. If equal, it will send all the received Ether to the seller (line 96). Then, the NFT will be transferred from the market to the buyer. However, since all the Ether are paid to the seller, there is nothing left for the payment of listingPrice. As a result, the execution will fail.
```solidity
// Transfers ownership of the item, as well as funds between parties
function purchaseExecution(
    address nftContract,
    uint256 itemId
)
    public
    payable
    nonReentrant
{
    uint price = idToMarketItem[itemId].price;
    uint tokenId = idToMarketItem[itemId].tokenId;
    require(msg.value == price, "Please submit the asking price in order to complete the purchase");
    bool sent = idToMarketItem[itemId].seller.send(msg.value);
    require(sent, "Failed to send Ether");
    IERC721(nftContract).transferFrom(address(this), msg.sender, tokenId);
    idToMarketItem[itemId].owner = payable(msg.sender);
    idToMarketItem[itemId].sold = true;
    _itemsSold.increment();
    payable(owner).transfer(listingPrice);
}
```

## Recommendation
Properly distribute the msg.value in the purchaseExecution() function (msg.vaule = listingPrice + price).
