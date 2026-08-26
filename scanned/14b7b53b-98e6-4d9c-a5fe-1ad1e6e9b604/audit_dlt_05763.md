# [C] # IOP _ ThunderNFT 34800 - [Smart Contract - Critical] Improper input validation in order update funct

## Summary
Severity: Critical
Chain: Smart contract
Component: ThunderNFT | IOP
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034800%20-%20%5BSmart%20Contract%20-%20Critical%5D%20Improper%20input%20validation%20in%20order%20update%20function%20leads%20to%20potential%20asset%20loss.md
Type: immunefi-boost

## Details
Target: https://github.com/ThunderFuel/smart-contracts/tree/main/contracts-v1/thunder\_exchange

## Description

## Brief/Intro

The update\_order function lacks proper validation for sell orders, allowing attackers to forge asset amounts without transferring the actual assets. This critical vulnerability in the order update mechanism could be exploited in production to create sell orders with artificially inflated asset amounts. Subsequently, attackers could cancel these fraudulent orders and withdraw assets they never actually deposited, potentially leading to significant theft of assets from the exchange or other users' funds, undermining the entire trading system's integrity and security.

## Vulnerability Details

To explain this vulnerability, let's first look at the code for the place\_order function. It is a payable function that checks `msg_asset_id()` and `msg_amount()` when a user creates a sell order.

```rust
    #[storage(read), payable]
    fn place_order(order_input: MakerOrderInput) {
        _validate_maker_order_input(order_input);

        let strategy = abi(ExecutionStrategy, order_input.strategy.bits());
        let order = MakerOrder::new(order_input);
        match order.side {
            Side::Buy => {
                // Buy MakerOrder (e.g. make offer)
                // Checks if user has enough bid balance
                let pool_balance = _get_pool_balance(order.maker, order.payment_asset);
                require(order.price <= pool_balance, ThunderExchangeErrors::AmountHigherThanPoolBalance);
            },
            Side::Sell => {
                // Sell MakerOrder (e.g. listing)
                // Checks if assetId and amount mathces with the order
                require(msg_asset_id() == AssetId::new(order.collection, order.token_id), ThunderExchangeErrors::AssetIdNotMatched);
                require(msg_amount() == order_input.amount, ThunderExchangeErrors::AmountNotMatched); // <---- proper checks here
            },
        }

        strategy.place_order(order);

        log(OrderPlaced {
            order
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034800%20-%20%5BSmart%20Contract%20-%20Critical%5D%20Improper%20input%20validation%20in%20order%20update%20function%20leads%20to%20potential%20asset%20loss.md_
