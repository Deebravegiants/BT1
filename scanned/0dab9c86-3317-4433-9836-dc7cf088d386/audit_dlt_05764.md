# [C] # IOP _ ThunderNFT 34930 - [Smart Contract - Critical] User can only trade token when ERC is used

## Summary
Severity: Critical
Chain: Smart contract
Component: ThunderNFT | IOP
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034930%20-%20%5BSmart%20Contract%20-%20Critical%5D%20User%20can%20only%20trade%20%20token%20when%20ERC%20is%20used.md
Type: immunefi-boost

## Details
Target: https://github.com/ThunderFuel/smart-contracts/tree/main/contracts-v1/libraries

## Description

## Brief/Intro

According to [discord chat history](https://discord.com/channels/787092485969150012/1271498128981495950/1273191123048988796), ERC1155 tokens are also in scope. In current implementation, there is a issue than when the order maker tries to trade more than 1 tokens for assetId\_X, he/she can only get 1 assetId\_X token.

Which will cause the user losses assets.

## Vulnerability Details

I'll use `Side::Buy` order as an example.

When a buyer calls [thunder\_exchange.place\_order](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/thunder_exchange/src/main.sw#L83-L109) to fill a `Side::Buy` order, he can set the amount of ERC1155 asset he wants to buy by [MakerOrderInput.amount](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/libraries/src/order_types.sw#L49).

Then the seller see the order, and he will call [thunder\_exchange.execute\_order](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/thunder_exchange/src/main.sw#L181-L193) to fill a `Side::Sell` order, and at the same time, the tx will sent the specified ERC1155 token along with the tx. Then in `thunder_exchange._execute_sell_taker_order`, [strategy.execute\_order](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/thunder_exchange/src/main.sw#L398) is called.

In [strategy\_fixed\_price\_sale.execute\_order](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/execution_strategies/strategy_fixed_price_sale/src/main.sw#L128-L152), [ExecutionResult::s1](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/execution_strategies/strategy_fixed_price_sale/src/main.sw#L146) is called to generate an `execution_result`.

As function [execution\_result.s1](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/libraries/src/execution_result.sw#L16-L34) shows, **the amount is always set to 1, which causes the issue**

```solidity
 16     pub fn s1(maker_order: MakerOrder, taker_order: TakerOrder) -> ExecutionResult {
 17         ExecutionResult {
 18             is_executable: (
 19                 (maker_order.side != taker_order.side) &&
 20                 (maker_order.maker != taker_order.taker) &&
 21                 (maker_order.maker == taker_order.maker) &&
 22                 (maker_order.nonce == taker_order.nonce) &&
 23                 (maker_order.price == taker_order.price) &&
 24                 (maker_order.token_id == taker_order.token_id) &&
 25                 (maker_order.collection == taker_order.collection) &&
 26                 (maker_order.end_time >= timestamp()) &&
 27                 (maker_order.start_time <= timestamp())
 28             ),
 29             collection: taker_order.collection,
 30             token_id: taker_order.token_id,
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034930%20-%20%5BSmart%20Contract%20-%20Critical%5D%20User%20can%20only%20trade%20%20token%20when%20ERC%20is%20used.md_
