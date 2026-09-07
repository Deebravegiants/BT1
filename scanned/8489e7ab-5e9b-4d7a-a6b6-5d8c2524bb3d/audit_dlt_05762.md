# [C] # IOP _ ThunderNFT 34736 - [Smart Contract - Critical] ERC tokens are stuck on the contract if more th

## Summary
Severity: Critical
Chain: Smart contract
Component: ThunderNFT | IOP
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034736%20-%20%5BSmart%20Contract%20-%20Critical%5D%20ERC%20tokens%20are%20stuck%20on%20the%20contract%20if%20more%20than%20%20supplied%20for%20Sell%20order.md
Type: immunefi-boost

## Details
Target: https://github.com/ThunderFuel/smart-contracts/tree/main/contracts-v1/libraries

## Description

## Brief/Intro

When a _Sell_ order is executed the amount of assets sold to the taker is always 1. Once an order is executed it is deleted. If there were more than 1 asset amount on that order they are locked in the exchange permanently

## Vulnerability Details

The Thunder exchange supports also ERC1155 tokens which could be provided during placement of the _Sell_ order by calling the `place_order()` method.

The contract validate if the order input data matches with the assets supplied to the contract by the seller using the following code:

```
require(msg_asset_id() == AssetId::new(order.collection, order.token_id), ThunderExchangeErrors::AssetIdNotMatched);
require(msg_amount() == order_input.amount, ThunderExchangeErrors::AmountNotMatched);
```

When a _Sell_ order is executed by calling the `execute_order()` method the `amount` to be sold is hardcoded to `1` in the `ExecutionResult` function `s1()` as per the following snippet:

```
    pub fn s1(maker_order: MakerOrder, taker_order: TakerOrder) -> ExecutionResult {
        ExecutionResult {
            is_executable: (
                [ . . . ]
            ),
            collection: taker_order.collection,
            token_id: taker_order.token_id,
            amount: 1,
            payment_asset: maker_order.payment_asset,
        }
    }
```

This means that only single asset is sold. Later on during the order processing, the order gets deleted in the `_execute_order()` function. Once an order is deleted:

1. it cannot be further executed, hence no more of the remaining assets can be sold.

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034736%20-%20%5BSmart%20Contract%20-%20Critical%5D%20ERC%20tokens%20are%20stuck%20on%20the%20contract%20if%20more%20than%20%20supplied%20for%20Sell%20order.md_
