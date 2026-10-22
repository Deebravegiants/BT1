# [M] Protocol owner is a single point of failure.

## Summary
Severity: Medium
Contest weight: 0.1879
Dataset id: 17389
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Protocol owner can arbitrarily and unilaterally create coordinators/products, update product/incentivizer/collateral addresses and change the various fees and minimum collateral requirements used by all the products and users of the protocol. This presents a critical single point of failure. If a protocol owner becomes malicious or compromised, the entire protocol is immediately at risk for all existing/future products and users. While the updation of critical parameters emit events, that only lets product owners and users react after the fact because these changes are not time-delayed. A scenario that affects future products/users is the updation of product/incentivizer/collateral contract addresses to malicious ones and creation of malicious/biased products/coordinators. A DoS scenario, for existing products/users, is the protocol owner increasing the minimum collateral to a high enough value which prevents deposits and withdrawals for certain accounts/products. The owner may increase the protocol fee split to 100% taking away the incentives for existing product owners. The owner may decrease the liquidation fee to a very low value making it uneconomical to liquidate under-collateralized accounts.

## Recommendation
While it has been communicated that the initial protocol ownership on product creation and other critical protocol aspects is part of the guarded launch strategy, the protocol owner should nevertheless be a reasonable threshold multisig (e.g. 4/7, 5/9) with diverse owners and (cold/hardware) wallets until it is backed by token-holder governance, i.e., it should certainly never be an EOA. The highest possible operational security measures should be taken for all multisig owners and wallets.
