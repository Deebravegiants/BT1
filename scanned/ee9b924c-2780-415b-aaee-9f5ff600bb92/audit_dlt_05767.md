# [C] # IOP _ ThunderNFT 34958 - [Smart Contract - Critical] Incorrect Setting of Amount in ExecutionResult

## Summary
Severity: Critical
Chain: Smart contract
Component: ThunderNFT | IOP
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034958%20-%20%5BSmart%20Contract%20-%20Critical%5D%20Incorrect%20Setting%20of%20Amount%20in%20ExecutionResult.md
Type: immunefi-boost

## Details
Target: https://github.com/ThunderFuel/smart-contracts/tree/main/contracts-v1/libraries

## Description

## Brief/Intro

The `ExecutionResult` in the libraries incorrectly sets the amount to a constant value of 1 in the `s1` function. If a victim places a buy-side order with an amount greater than 1, the order is placed successfully. However, after execution, the amount is incorrectly changed to 1, allowing the attacker to fulfill the order with only 1 asset, resulting in a loss for the victim.

## Vulnerability Details

When Thunder Exchange executes an sell-side taker order, it receives the execution result from `strategy.execute_order(order)`. This function finds the matched order and [generates the execution result](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/execution_strategies/strategy_fixed_price_sale/src/main.sw#L146). During this process, several checks are performed, but the amount is not properly validated. Instead, [the amount is set to a constant value of 1](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/libraries/src/execution_result.sw#L31), regardless of the original order's amount. When Thunder Exchange receives the execution result, it checks if the asset and amount provided by the taker [match those in the execution result](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/thunder_exchange/src/main.sw#L404), which incorrectly shows an amount of 1. This allows the taker to fulfill the order with just 1 corresponding asset, disregarding the original order's amount.

A prerequisite for this attack is that victim must placed a buy-side order with amount greater than 1. In Fuel, NFTs differ from those in Ethereum as they are native assets, blurring the boundary between NFTs and fungible tokens (FTs). This ambiguity makes it plausible that users might use this protocol to sell FTs. Furthermore, fractional NFTs exist in Ethereum, so we can't strongly assert that there is only one NFT for each asset (contract, token\_id pair). Therefore, this scenario is highly likely to occur.

## Impact Details

An attacker can take any buy-side order by providing only 1 asset, even if the original order required a larger quantity. This results in the victim not receiving the expected amount of assets they ordered.

## References

https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/libraries/src/execution\_result.sw#L31 https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/execution\_strategies/strategy\_fixed\_price\_sale/src/main.sw#L146 https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/thunder\_exchange/src/main.sw#L404

## Proof of concept

## POC

This PoC demonstrates a scenario where a victim places a buy-side order with a price of 10, demanding 10 base assets, which should typically result in no loss and no profit for the victim. However, as shown in this PoC, an attacker can take this order by providing only 1 base asset, causing the victim to lose 9 base assets.

### Prerequisite

To demonstrate the impact, we need to set up two accounts: an admin account, which will set up the Thunder Exchange contract and also act as the victim placing an order, and an attacker account, which will later take the order with less asset amount than required by the victim.

**Attacker Account**

* Account(fuel): fuel16r69m48pwg4c8dtlnpze2m95t2fws4vwdju7w7sm9ztj459c0ekqs6xjg5
* Account: 0xd0f45dd4e1722b83b57f9845956cb45a92e8558e6cb9e77a1b28972ad0b87e6c
* Private Key: 306a75f0093834948e363ece5ba1b5a7eaad99f2fc9ab976ba01c2dbea3320f6


_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034958%20-%20%5BSmart%20Contract%20-%20Critical%5D%20Incorrect%20Setting%20of%20Amount%20in%20ExecutionResult.md_
