# [C] # IOP _ ThunderNFT 34949 - [Smart Contract - Critical] Missing proper validation when updating order

## Summary
Severity: Critical
Chain: Smart contract
Component: ThunderNFT | IOP
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034949%20-%20%5BSmart%20Contract%20-%20Critical%5D%20Missing%20proper%20validation%20when%20updating%20order.md
Type: immunefi-boost

## Details
Target: https://github.com/ThunderFuel/smart-contracts/tree/main/contracts-v1/thunder\_exchange

## Description

## Brief/Intro

Thunder Exchange lacks proper validation during the `update_order` function for sell-side orders. When transferring assets back to the user, the exchange may transfer an incorrect amount of previously stored assets, allowing an attacker to steal assets from Thunder Exchange.

## Vulnerability Details

When placing a sell-side order, Thunder Exchange [checks](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/thunder_exchange/src/main.sw#L96) if the user provides the correct asset and amount that match the details claimed in the order. However, when updating a sell-side order, [proper validation is missing](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/thunder_exchange/src/main.sw#L124). The only check performed is [`_validate_updated_order`](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/execution_strategies/strategy_fixed_price_sale/src/main.sw#L413) when calling the strategy's `update_order` function, which verifies that the maker, collection, token\_id, and payment\_asset remain the same, but it does not check for the amount.

When canceling the order, Thunder Exchange [transfers back](https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/thunder_exchange/src/main.sw#L161) the corresponding asset and amount based on the updated order. Therefore, an attacker can exploit this by placing a sell-side order with the minimum asset amount, then updating the order to a higher amount, and finally canceling it to steal the additional assets from Thunder Exchange.

A prerequisite for this attack is that there must be multiple instances of the same asset stored in Thunder Exchange. In Fuel, NFTs differ from those in Ethereum as they are native assets, blurring the boundary between NFTs and fungible tokens (FTs). This ambiguity makes it plausible that users might use this protocol to sell FTs. Furthermore, fractional NFTs exist in Ethereum, so we can't strongly assert that there is only one NFT for each asset (contract, token\_id pair). Therefore, this scenario is highly likely to occur.

## Impact Details

An attacker can steal assets from Thunder Exchange by placing a sell-side order with a small amount, then updating the order to a higher amount without proper validation, and finally canceling the order to receive the increased amount. This exploit is possible when there are multiple instances of one asset (i.e., not unique) in Thunder Exchange.

## References

https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/thunder\_exchange/src/main.sw#L124 https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/execution\_strategies/strategy\_fixed\_price\_sale/src/main.sw#L413 https://github.com/ThunderFuel/smart-contracts/blob/260c9859e2cd28c188e8f6283469bcf57c9347de/contracts-v1/thunder\_exchange/src/main.sw#L161

## Proof of concept

## Proof of Concept

### Prerequisite

To demonstrate the impact, we need to set up two accounts: an admin account to set up the Thunder Exchange contract and an attacker account to exploit the vulnerability and steal funds from Thunder Exchange.

**Attacker Account**

* Account: 0xd0f45dd4e1722b83b57f9845956cb45a92e8558e6cb9e77a1b28972ad0b87e6c
* Private Key: 306a75f0093834948e363ece5ba1b5a7eaad99f2fc9ab976ba01c2dbea3320f6

**Admin Account**

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034949%20-%20%5BSmart%20Contract%20-%20Critical%5D%20Missing%20proper%20validation%20when%20updating%20order.md_
