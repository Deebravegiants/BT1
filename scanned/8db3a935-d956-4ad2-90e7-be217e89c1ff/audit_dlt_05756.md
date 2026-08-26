# [M] # IOP _ ThunderNFT 34567 - [Smart Contract - Medium] users with current bid order can not update their

## Summary
Severity: Medium
Chain: Smart contract
Component: ThunderNFT | IOP
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034567%20-%20%5BSmart%20Contract%20-%20Medium%5D%20users%20with%20current%20bid%20order%20can%20not%20update%20their%20order%20when%20payment%20token%20changed.md
Type: immunefi-boost

## Details
Target: https://github.com/ThunderFuel/smart-contracts/tree/main/contracts-v1/thunder\_exchange

## Description

## Brief/Intro

the function `update_order` meant to allow users with current active bid to update their order important input, however there is critical check that prevent users to update their bid and they all forced to cancel their bid, this will lead to lose of gas only for buy order users. this happens because the update\_order calls the update\_order in the fixed strategy which in return it calls the \_update\_buy\_order which checks if the payment asset in unchanged, the payment asset is same asset that set in whitelist when assetManger call add asset or remove it by calling remove asset.

same thing can be applied to sell order users which is more critical situation compared to buy order users, we can take the steps below that can happen when the paymentAsset removed and new asset added:

* Alice create sell order(listing NFT) by calling place\_order with paymentAsset == USDT.
* 10 users create buy order to bid on alice NFT, and their payment asset == USDT.
* for some reason, USDT removed from whitelisted address by calling the `assetManger.sw#remove_asset` and ETH added as paymentAsset by calling `add_asset` function.
* because of the check`(order.unwrap().payment_asset == updated_order.payment_asset)` which check the payment asset of old order and updated one in `_validate_updated_order` which invoked by \_update\_buy and \_update\_sell alice and all other 10 users with bid order can not update their bid order payment asset to eth, same true for alice.
* this way alice and other users are forced to remove their orders(cancle it) and re create same order again and add new bid on the alice NFT which lead to lose of gas too.

## Vulnerability Details

the function update\_order implemented as below:

```sway
    #[storage(read), payable]
    fn update_order(order_input: MakerOrderInput) {
        _validate_maker_order_input(order_input);

        let strategy = abi(ExecutionStrategy, order_input.strategy.bits());
        let order = MakerOrder::new(order_input);
        match order.side {
            Side::Buy => {
                // Checks if user has enough bid balance
                let pool_balance = _get_pool_balance(order.maker, order.payment_asset);
                require(order.price <= pool_balance, ThunderExchangeErrors::AmountHigherThanPoolBalance);
            },
            Side::Sell => {}, // if order is selling nft then nothing to check for
        }

        strategy.update_order(order);

```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034567%20-%20%5BSmart%20Contract%20-%20Medium%5D%20users%20with%20current%20bid%20order%20can%20not%20update%20their%20order%20when%20payment%20token%20changed.md_
