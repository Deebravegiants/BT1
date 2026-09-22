# [M] 6.3 Order Salt Problems

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Specification Changed

The salt is effectively a field of an order that allows different orders of the same asset types from the
same maker to be distinguishable from each other. This field is also part of the hashKey of the order that
is used to track the filling of the order. However, due to the lack of Asset values in the hashKey, the
same value for salt can be resubmitted with higher-order take value, and thus lead to multiple full filling of
the same order. For example, an order that makes 20 take X after filling can be resubmitted with the
same salt and higher take limit: make 30 take 2X. Note that after cancellation the salt becomes unusable
for the maker. From a specification point of view, it the order with same hashKey shouldn't be fully filled
multiple times.

```
function hashKey(Order memory order) internal pure returns (bytes32) {
return keccak256(abi.encode(
order.maker,
LibAsset.hash(order.makeAsset.assetType),
LibAsset.hash(order.takeAsset.assetType),
order.salt
));
}
```
Specification corrected:

The behavior was documented and properly described in exchange-v2/readme.md.
