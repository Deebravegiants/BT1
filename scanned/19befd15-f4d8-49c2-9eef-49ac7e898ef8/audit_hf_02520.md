# [M] Potential DoS Against auction()

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 13441
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The XNFT contract provides an auction() routine for users to bid for the auction of the liquidated order. While examining the current auction logic, we notice the existence of potential DoS (denial-of-service) that needs to be avoided in the implementation.

To elaborate, we show below the implementation of the auction() routine. It will repay the liquidation price back to the liquidator or repay the auction price back to the previous bidder. However, it comes to our attention that the auction() routine may always revert if the underlying token is ETH and the liquidator or the previous bidder refuses to receive ETH. As a result, the liquidator or the previous bidder will finally win the auction and withdraw the NFT after the auction.
```solidity
function auction(uint256 orderId, uint256 amount) payable external nonReentrant whenNotPaused(3){
    require(isOrderLiquidated(orderId), "this order is not a liquidation order");
    LiquidatedOrder storage liquidatedOrder = allLiquidatedOrder[orderId];
    require(liquidatedOrder.auctionWinner == address(0), "the order has been withdrawn");
    require(!liquidatedOrder.isPledgeRedeem, "redeemed by the pledgor");
    Order storage _order = allOrders[orderId];
    if(IXToken(liquidatedOrder.xToken).underlying() == ADDRESS_ETH){
        amount = msg.value;
        uint256 price;
        if(liquidatedOrder.auctionAccount == address(0)){
            price = liquidatedOrder.liquidatedPrice;
        }else{
            price = liquidatedOrder.auctionPrice;
        }
        bool isPledger = auctionAllowed(_order.pledger, msg.sender, _order.collection, liquidatedOrder.liquidatedStartTime, price, amount);
        if(isPledger){
            uint256 fine = price.mul(pledgerFineRate).div(1e18);
            Public
            uint256 _amount = liquidatedOrder.liquidatedPrice.add(fine); // Luck: price.add(fine) or possible _amount < price?
            doTransferIn(liquidatedOrder.xToken, payable(msg.sender), _amount);
            uint256 rewardFirst = fine.mul(rewardFirstRate).div(1e18);
            if(liquidatedOrder.auctionAccount == address(0)){
                doTransferOut(liquidatedOrder.xToken, payable(liquidatedOrder.liquidator), rewardFirst);
                uint256 rewardLast = fine.mul(rewardLastRate).div(1e18);
                doTransferOut(liquidatedOrder.xToken, payable(liquidatedOrder.auctionAccount), (rewardLast + liquidatedOrder.auctionPrice));
                addUpIncomeMap[liquidatedOrder.xToken] = addUpIncomeMap[liquidatedOrder.xToken] + (fine - rewardFirst - rewardLast);
            }else{
                doTransferOut(liquidatedOrder.xToken, payable(liquidatedOrder.liquidator), (liquidatedOrder.liquidatedPrice + rewardFirst));
                addUpIncomeMap[liquidatedOrder.xToken] = addUpIncomeMap[liquidatedOrder.xToken] + (fine - rewardFirst);
                transferNftInternal(address(this), msg.sender, _order.collection, _order.tokenId, _order.nftType);
                _order.isWithdraw = true;
                liquidatedOrder.isPledgeRedeem = true;
                liquidatedOrder.auctionWinner = msg.sender;
                liquidatedOrder.auctionAccount = msg.sender;
                liquidatedOrder.auctionPrice = _amount;
                emit AuctionNFT(orderId, liquidatedOrder.xToken, msg.sender, amount, true);
                emit WithDraw(_order.collection, _order.tokenId, orderId, _order.pledger, msg.sender);
            }
        }else{
            doTransferIn(liquidatedOrder.xToken, payable(msg.sender), amount);
            if(liquidatedOrder.auctionAccount == address(0)){
                doTransferOut(liquidatedOrder.xToken, payable(liquidatedOrder.liquidator), liquidatedOrder.liquidatedPrice); // Luck: if the XToken is ETH market, a malicious user may block new auction refusing to accept ETH
            }else{
                doTransferOut(liquidatedOrder.xToken, payable(liquidatedOrder.auctionAccount), liquidatedOrder.auctionPrice);
            }
            liquidatedOrder.auctionAccount = msg.sender;
            liquidatedOrder.auctionPrice = amount;
            emit AuctionNFT(orderId, liquidatedOrder.xToken, msg.sender, amount, false);
        }
    }
}

function doTransferOut(address xToken, address payable account, uint256 amount) internal{
    if(amount == 0) return;
    if (IXToken(xToken).underlying() != ADDRESS_ETH) {
        IERC20(IXToken(xToken).underlying()).safeTransfer(account, amount);
    } else {
        account.transfer(amount);
    }
}
```
Note the same issue exists in the XNFT::withdrawNFT() routine.

## Recommendation
Avoid the above denial-of-service risk in the above auction()/withdrawNFT() routines.
