# [M] Unsold tokens from a FPAM auction, will be stuck in the contract forever

## Summary
Severity: Medium
Contest weight: 0.5939
Dataset id: 22637
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Axis-Finance protocol allows sellers to create two types of auctions: FPAM & EMPAM. An FPAM auction allows sellers to set a price, and a maxPayout, as well as create a prefunded auction. The seller of a FPAM auction can cancel it while it is still active by calling the cancel function which in turn calls the cancelAuction() function. If the auction is prefunded, and canceled while still active, all remaining funds will be transferred back to the seller. The problem arises if an FPAM prefunded auction is created, not all of the prefunded supply is bought by users, and the auction concludes. There is no way for the baseTokens still in the contract, to be withdrawn from the protocol, and they will be forever stuck in the Axis-Finance protocol. As can be seen from the below code snippet cancelAuction() function checks if an auction is concluded, and if it is the function reverts.
```solidity
function _revertIfLotConcluded(uint96 lotId_) internal view virtual {
    // Beyond the conclusion time
    if (lotData[lotId_].conclusion < uint48(block.timestamp)) {
        revert Auction_MarketNotActive(lotId_);
    }
    // Capacity is sold-out, or cancelled
    if (lotData[lotId_].capacity == 0) revert Auction_MarketNotActive(lotId_);
}
```
Gist After following the steps in the above mentioned gist add the following test to the AuditorTests.t.sol file
```solidity
function test_FundedPriceAuctionStuckFunds() public {
    vm.startPrank(alice);
    Keycode keycode = keycodeFromVeecode(veecode);
    bytes memory _derivativeParams = "";
    uint96 lotCapacity = 75_000_000_000e18; // this is 75 billion tokens
    mockBaseToken.mint(alice, lotCapacity);
    mockBaseToken.approve(address(auctionHouse), type(uint256).max);
    FPAM.FundedPriceAuctionParams memory myStruct =
        FPAM.FundedPriceAuctionParams({
            price: uint96(1e18),
            maxPayoutPercent: uint24(1e5)
        });
    Auctioneer.RoutingParams memory routingA = Auctioneer.RoutingParams({
        auctionType: keycode,
        baseToken: mockBaseToken,
        quoteToken: mockQuoteToken,
        curator: curator,
        callbacks: ICallback(address(0)),
        callbackData: abi.encode(""),
        derivativeType: toKeycode(""),
        derivativeParams: _derivativeParams,
        wrapDerivative: false,
        prefunded: true
    });
    Auction.AuctionParams memory paramsA = Auction.AuctionParams({
        start: 0,
        duration: 1 days,
        capacityInQuote: false,
        capacity: lotCapacity,
        implParams: abi.encode(myStruct)
    });
    string memory infoHashA;
    auctionHouse.auction(routingA, paramsA, infoHashA);
    vm.stopPrank();
    vm.startPrank(bob);
    uint96 fundingBeforePurchase;
    uint96 fundingAfterPurchase;
    (,fundingBeforePurchase,,,,,,,) = auctionHouse.lotRouting(0);
    console2.log("Here is the funding normalized before purchase: ", fundingBeforePurchase/1e18);
    mockQuoteToken.mint(bob, 10_000_000_000e18);
    mockQuoteToken.approve(address(auctionHouse), type(uint256).max);
    Router.PurchaseParams memory purchaseParams = Router.PurchaseParams({
        recipient: bob,
        referrer: address(0),
        lotId: 0,
        amount: 10_000_000_000e18,
        minAmountOut: 10_000_000_000e18,
        auctionData: abi.encode(0),
        permit2Data: ""
    });
    bytes memory callbackData = "";
    auctionHouse.purchase(purchaseParams, callbackData);
    (,fundingAfterPurchase,,,,,,,) = auctionHouse.lotRouting(0);
    console2.log("Here is the funding normalized after purchase: ", fundingAfterPurchase/1e18);
    console2.log("Balance of seller of quote tokens: ", mockQuoteToken.balanceOf(alice)/1e18);
    console2.log("Balance of bob in base token: ", mockBaseToken.balanceOf(bob)/1e18);
    console2.log("Balance of auction house in base token: ", mockBaseToken.balanceOf(address(auctionHouse)) /1e18);
    skip(86401);
    vm.stopPrank();
    vm.startPrank(alice);
    vm.expectRevert(
        abi.encodeWithSelector(Auction.Auction_MarketNotActive.selector, 0)
    );
    auctionHouse.cancel(uint96(0), callbackData);
    vm.stopPrank();
}
```
Logs:
Here is the funding normalized before purchase:
Here is the funding normalized after purchase:
Balance of seller of quote tokens:
Balance of bob in base token:
Balance of auction house in base token:
To run the test use: forge test -vvv --mt test_FundedPriceAuctionStuckFunds
If a prefunded FPAM auction concludes and there are still tokens, not bought from the users, they will be stuck in the Axis-Finance protocol.

## Recommendation
Implement a function, that allows sellers to withdraw the amount left for a prefunded FPAM auction they have created, once the auction has concluded.
