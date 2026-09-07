# [M] # IOP _ ThunderNFT 34714 - [Smart Contract - Medium] owner of NFT who have sell orderlisting NFT can n

## Summary
Severity: Medium
Chain: Smart contract
Component: ThunderNFT | IOP
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034714%20-%20%5BSmart%20Contract%20-%20Medium%5D%20owner%20of%20NFT%20who%20have%20sell%20orderlisting%20NFT%20can%20not%20accept%20any%20bid%20offers.md
Type: immunefi-boost

## Details
Target: https://github.com/ThunderFuel/smart-contracts/tree/main/contracts-v1/thunder\_exchange

## Description

## Brief/Intro

the function `execute_order` meant to allow users to buy the NFT directly by sending the listed price for the nft and it allows seller of the NFT to accept specific bid offers. however its impossible for the seller/owner of the NFT to accept any bids because of the check that exist in the `_execute_sell_taker_order` function which checks if the msg\_asset() is valid when the user calls the execute\_order function, its impossible for the seller to have the asset\_id(the NFT) since the `place_order` function ask the seller to transfer the NFT to the thunder exchange contract, this way its impossible for seller to accept any bids.

* we believe this can be high severity report instead of medium but we will go with medium severity and let the team/immunefi decide the valid severity for this report.

## Vulnerability Details

when NFT owner want want to list its NFT the function `place_order` should be called with Side == sell:

```sway
    /// Places MakerOrder by calling the strategy contract
    /// Checks if the order is valid
    #[storage(read), payable] // @audit when user set sell order(listing) the function force the user to sent its NFT in checks below
    fn place_order(order_input: MakerOrderInput) {
        _validate_maker_order_input(order_input); // sanity checks 

        let strategy = abi(ExecutionStrategy, order_input.strategy.bits());
        let order = MakerOrder::new(order_input);

        match order.side {
            Side::Buy => { //users make offer for specific nft(bid)
                // Buy MakerOrder (e.g. make offer)
                // Checks if user has enough bid balance
                let pool_balance = _get_pool_balance(order.maker, order.payment_asset); // get the maker balance of the payment asset
                require(order.price <= pool_balance, ThunderExchangeErrors::AmountHigherThanPoolBalance); // example: price is 5 eth and user have 6 eth
            },
            Side::Sell => { 
                // Sell MakerOrder (e.g. listing)
                // Checks if assetId and amount mathces with the order
                //@audit forced to send the NFT
                require(msg_asset_id() == AssetId::new(order.collection, order.token_id), ThunderExchangeErrors::AssetIdNotMatched);
                require(msg_amount() == order_input.amount, ThunderExchangeErrors::AmountNotMatched);
            }, //transfer the NFT to this contract
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034714%20-%20%5BSmart%20Contract%20-%20Medium%5D%20owner%20of%20NFT%20who%20have%20sell%20orderlisting%20NFT%20can%20not%20accept%20any%20bid%20offers.md_
