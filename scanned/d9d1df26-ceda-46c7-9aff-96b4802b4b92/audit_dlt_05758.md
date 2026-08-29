# [C] # IOP _ ThunderNFT 34629 - [Smart Contract - Critical] Theft of Deposited Funds

## Summary
Severity: Critical
Chain: Smart contract
Component: ThunderNFT | IOP
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034629%20-%20%5BSmart%20Contract%20-%20Critical%5D%20Theft%20of%20Deposited%20Funds.md
Type: immunefi-boost

## Details
Target: https://github.com/ThunderFuel/smart-contracts/tree/main/contracts-v1/thunder\_exchange

## Description

## Thunder Exchange

### Theft of Deposited Funds

#### Description

A critical vulnerability exists that enables a malicious actor to steal all deposited non-unique tokens (e.g., tokens following the `ERC1155` standard) listed for sale.

### Root Cause

As discussed in our Discord exchange, the `Order.amount` field was introduced to accommodate ERC1155-style tokens:

> Hi! Yes, amount is added in case of Erc1155 style token standard

However, when updating a sell order, there is no validation to ensure that the order maker has deposited the required additional tokens into the exchange.

In the code snippet below, you can see that the `update_order` function does not check if additional tokens have been deposited when modifying an existing order:

```rs
    fn update_order(order_input: MakerOrderInput) {
        // ...
        match order.side {
            // ...
            Side::Sell => {},
        }
        // ...
    }
```

This omission allows an attacker to modify the `amount` variable in the order without actually depositing the corresponding tokens.

For comparison, the `place_order` function does perform this validation:

```rs
```

_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034629%20-%20%5BSmart%20Contract%20-%20Critical%5D%20Theft%20of%20Deposited%20Funds.md_
