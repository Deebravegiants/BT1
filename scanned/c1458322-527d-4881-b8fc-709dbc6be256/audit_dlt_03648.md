# [M] An attacker can flash steal rented NFTs by bypassing `_executionInvariantChecks()` checks.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-02-renft-mitigation
Published: 2024-03-04
Source: https://github.com/code-423n4/2024-02-renft-mitigation-findings/issues/29
Type: code-finding

## Details
# Lines of code

https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L590


# Vulnerability details


# Impact
This vulnerability allows an attacker to temporarily steal (flash steal) an NFT allowing him to bypass the hooks enforced by the lender of the NFT. Similar impact to https://github.com/code-423n4/2024-01-renft-findings/issues/466



# The vulnerability & Proof of concept

The exploitation of this vulnerability relies on multiple primitives however the most important exploit primitive would be that the [`_executionInvariantChecks()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L590) function check can be bypassed if the address of the offerer of the rental order is the same as the address of the borrower (recipient). In this case, the seaport conduit does not conduct any token transfers and these transfers/executions aren't included in the `seaportPayload.totalExecutions` array which is fed into the [`_executionInvariantChecks()`](https://github.com/re-nft/smart-contracts/blob/97e5753e5398da65d3d26735e9d6439c757720f5/src/policies/Create.sol#L590) function. [`From seaport docs on matchOrders`](https://github.com/ProjectOpenSea/seaport/blob/main/docs/SeaportDocumentation.md#match-orders)

> Use either conduit or Seaport directly to source approvals, depending on the original order type

> Ignore each execution where to == from

Because this is a sophisticated exploit, I'll break it down step by step:

0. Let's say the attacker is going to be hijacking NFT ID 5 in a legitimate `PAY` order lent by Alice. This will be a legitimate order with the following parameters:
    - Offer item #1: NFT ID 5
    - Offer item #2: 100 ERC20 tokens
    - Lender: Alice
    - Borrower: address_of_attackers_Rental_Safe

1. The attacker will construct a malicious `PAY` order. The offerItems of the order to be NFT ID 5, the 100 ERC20 tokens and the offerer (lender) of the order would be the attacker's rental safe, and the fulfiller would also be the rental safe. So in conclusion, the order will have the following parameters:
    
    - Offer item #1: NFT ID 5
    - Offer item #2: 100 ERC20 tokens
    - Lender: address_of_attackers_Rental_Safe
    - Borrower: address_of_attackers_Rental_Safe

2. The attacker will construct a useless `PAY` order and specify a zone contract he controls to be called. This order's only use is that it'll allow us to execute any zone contract we specify to it.


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-02-renft-mitigation-findings/issues/29_
