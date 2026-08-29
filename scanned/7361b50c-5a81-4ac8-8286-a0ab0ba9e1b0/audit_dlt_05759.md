# [C] # IOP _ ThunderNFT 34630 - [Smart Contract - Critical] Incorrect Token Sale Amount

## Summary
Severity: Critical
Chain: Smart contract
Component: ThunderNFT | IOP
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034630%20-%20%5BSmart%20Contract%20-%20Critical%5D%20Incorrect%20Token%20Sale%20Amount.md
Type: immunefi-boost

## Details
Target: https://github.com/ThunderFuel/smart-contracts/tree/main/contracts-v1/libraries

## Description

## Thunder Exchange

### Incorrect Token Sale Amount

#### Description

An issue has been identified that allows a malicious actor to sell only one token, even if the Buy Order specifies a greater quantity. This vulnerability effectively bypasses the intended order amount.

### Root Cause

As discussed in our Discord exchange, the `Order.amount` field was introduced to accommodate ERC1155-style tokens:

> Hi! Yes, amount is added in case of Erc1155 style token standard

This clearly states that the `Order.amount` can be greater than 1. However, when executing an order, the `ExecutionResult` has a hardcoded amount of 1:

```rs
    pub fn s1(maker_order: MakerOrder, taker_order: TakerOrder) -> ExecutionResult {
        ExecutionResult {
            // ...
            amount: 1, // 
            // ...
        }
    }
```

As a result, the specified amount in the Order is effectively ignored.

### Impact

This issue has two significant impacts:

#### Buy Order


_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ThunderNFT%20%7C%20IOP/IOP%20_%20ThunderNFT%2034630%20-%20%5BSmart%20Contract%20-%20Critical%5D%20Incorrect%20Token%20Sale%20Amount.md_
