# [M] `RentPayload`'s signature can be replayed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-01-renft
Published: 2024-01-16
Source: https://github.com/code-423n4/2024-01-renft-findings/issues/162
Type: code-finding

## Details
# Lines of code

https://github.com/re-nft/smart-contracts/blob/3ddd32455a849c3c6dc3c3aad7a33a6c9b44c291/src/policies/Create.sol#L760-L763


# Vulnerability details

## Impact
A malicious user could potentially fulfill all `PAY` orders that own the same value of `zonehash`

## Proof of Concept
The rental process in `reNFT` can simply be described as follows:
1. `lender` create either `BASE` or `PAY` order, which includes a `zoneHash`.
2. `renter` fulfills the rental order by providing certain items, including `fulfiller`, `payload`(a structured data of `RentPayload`), and its corresponding signature.
3. Once the rental order is created, `Create#validateOrder()` will be executed to verify if the rental order is valid:
   - decode `payload` and its `signature` from `zoneParams.extraData`
   - Check if the signature is expired by comparing `payload.expiration` and `block.timestamp`
   - Recover the signer from `payload` and its `signature` and check if the signer is protocol signer
   - check if `zonehash` is equal to the derived hash of `payload.metadata`

Let's take a look at `RentPayload` and its referenced structures:
```solidity
struct RentPayload {
    OrderFulfillment fulfillment;
    OrderMetadata metadata;
    uint256 expiration;
    address intendedFulfiller;
}
struct OrderFulfillment {
    // Rental wallet address.
    address recipient;
}
struct OrderMetadata {
    // Type of order being created.
    OrderType orderType;
    // Duration of the rental in seconds.
    uint256 rentDuration;
    // Hooks that will act as middleware for the items in the order.
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-01-renft-findings/issues/162_
