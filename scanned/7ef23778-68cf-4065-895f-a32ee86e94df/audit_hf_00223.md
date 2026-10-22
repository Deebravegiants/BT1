# [M] isResolverCached

## Summary
Severity: Medium
Contest weight: 0.4895
Dataset id: 1148
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While there is no loss of funds, removing an operator will cause the cache functionality to be permanently broken. If there was a function that had a modifier which requires the cache to be synced before the function can be called, it would not be callable as well.

The underlying issue is how the `bytes32` operator is removed from the array when `removeOperator()` is called. Its value gets deleted (set to 0x0), but isn’t taken out of the array.

## Proof of Concept
For ease of reading, we use abbreviated strings like `0xA`, `0xB` for `bytes32` and `address` types.

1. Import 3 operators by calling `OperatorResolver.importOperators([0xA, 0xB, 0xC], [0x1, 0x2, 0x3)`.
2. Call `NestedFactory.addOperator()` 3 times to push these 3 operators into the `operators` state variable.
3. Call `NestedFactory.rebuildCache()` to build the cache.
4. Let’s say the second operator `0xB` is to be removed. Taking reference from the `removeOperator.ts` script, `OperatorResolver.importOperators([0xA, 0xB, 0xC], [0x1, 0x2, 0x3)` is called first. This works because OperatorResolver uses a mapping(bytes32 ⇒ address) to represent the operators. Hence, by setting `0xB`’s destination address to be the null address, it is like as if he was never an operator.
5. Call `NestedFactory.rebuildCache()` to rebuild the cache. `resolverAddressesRequired()` will return `[0xA, 0xB, 0xC]`. `0xB` will be removed from `addressCache` because `resolver.getAddress(0xB)` returns 0x000 since it has been deleted from the OperatorResolver.
6. Call `NestedFactory.removeOperator(0xB)`. The `operators` array now looks like this: `[0xA, 0x0, 0xC]`.
7. When you try to call `NestedFactory.isResolverCached`, it will always return false because of the null `bytes32` value, where `addressCache[0x0]` will always return the null address.

## Recommendation
Instead of doing an element deletion, it should be replaced with the last element, then have the last element popped in `removeOperator()`.

```solidity
function removeOperator(bytes32 operator) external override onlyOwner {
	for (uint256 i = 0; i < operators.length; i++) {
		if (operators[i] == operator) {
			operators[i] = operators[operators.length - 1];
			operators.pop();
			break;
		}
	}
}
```

Duplicated : #58

Taking this issue apart as a non-duplicate, for finding the most severe consequence of the incorrect implementation.
