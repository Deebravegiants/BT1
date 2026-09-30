# [H] Possible Front-Running for ChronosMarketplace::buyNow()

## Summary
Severity: High
Contest weight: 0.6107
Dataset id: 11820
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.3, the ChronosMarketplace contract supports the Fixed Price trading mode. The buyer can purchase a listed NFT with a fixed price (specified by the owner of the NFT) via buyNow(). While examining its logic, we observe it is vulnerable to the possible front-running attack.

To elaborate, we show below the related code snippet of the contract. A malicious actor can list his NFT with a very low price via listNftForFixed(). If a user wants to purchase the NFT with the low price via buyNow(), the malicious actor may front-run changeSaleInfo() to make the NFT price higher. After that, the buyer will suffer from an unexpected loss.
```solidity
function changeSaleInfo(
    uint256 _saleId,
    uint256 _saleDuration,
    address _paymentToken,
    uint256 _price
) external override nonReentrant whenNotPaused {
    sellInfo.startTime = block.timestamp;
    sellInfo.endTime = sellInfo.startTime + _saleDuration;
    sellInfo.paymentToken = _paymentToken;
    sellInfo.price = _price;
}

/// @inheritdoc IChronosMarketPlace
function buyNow(
    uint256 _saleId
) external override nonReentrant whenNotPaused {
    IERC20(saleInfo.paymentToken).safeTransferFrom(
        buyer,
        saleInfo.seller,
        saleInfo.price - fee
    );
    IERC20(saleInfo.paymentToken).safeTransferFrom(buyer, treasury, fee);
    IERC721(saleInfo.nft).safeTransferFrom(
        address(this),
        buyer,
        saleInfo.tokenId
    );
    emit Bought(_saleId, saleInfo.buyer);
}
```
Note another routine, i.e., buyNowWithETH(), shares the same issue.

## Recommendation
Apply necessary anti-frontrunning mechanism to above-mentioned routines.
