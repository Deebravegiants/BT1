# [C] Chain re-orgs may facilitate improper order fulfillment

## Summary
Severity: Critical
Contest weight: 0.6198
Dataset id: 14846
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When an AP offer is created, only the offer hash is indexed to store the total amount of input tokens to be deposited during fulfillment(s). Upon fulfillment, the entire APOffer struct is provided in the call.
There are two notable values that can be altered such that abi.encodePacked() returns the same encoded data to be hashed.
These are address[] incentivesRequested and uint256[] incentiveAmountsRequested:
```solidity
struct APOffer {
    uint256 offerID;
    uint256 targetMarketID;
    address ap;
    address fundingVault;
    uint256 quantity;
    uint256 expiry;
    address[] incentivesRequested;
    uint256[] incentiveAmountsRequested;
}
```
When using abi.encodePacked(), arrays are encoded in place and without any of the typical data expected in dynamic array types.
Hence, when fulfilling an AP offer, getOfferHash() returns the same hash value if we alter the length of APOffer.incentivesRequested and APOffer.incentiveAmountsRequested.
Instead, if we pass an empty array for APOffer.incentivesRequested and prepend all of the incentive addresses to APOffer.incentiveAmountsRequested as uint256 array elements, then _fillAPOffer() will calculate the same hash and order fulfillment will be processed. Because the two arrays are not verified to be of the same length, we end up skipping all incentives because numIncentives is zero.
As a result, the deposit recipe will still execute without offering up any incentives.
When an IP offer is fulfilled, an offerHash parameter must be provided which allows for the IPOffer to be retrieved from storage. As all details are stored, there is no possibility of abusing the hash malleability of abi.encodePacked().

## Recommendation
Avoid using abi.encodePacked() when calculating the hash of an AP offer. It's also worth renaming the getOfferHash() implementations to clarify if an IP or AP offer is being hashed.
